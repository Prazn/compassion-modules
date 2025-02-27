##############################################################################
#
#    Copyright (C) 2016-2022 Compassion CH (http://www.compassion.ch)
#    Releasing children from poverty in Jesus' name
#    @author: Emanuel Cino <ecino@compassion.ch>
#
#    The licence is in the file __manifest__.py
#
##############################################################################
import logging
from collections import OrderedDict
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models

logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = "account.move"

    communication_id = fields.Many2one(
        "partner.communication.job",
        "Thank you letter",
        ondelete="set null",
        readonly=True,
        copy=False,
    )
    avoid_thankyou_letter = fields.Boolean(
        help="Check to disable thank you letter for donation",
    )

    def action_invoice_paid(self):
        """Generate a Thank you Communication when invoice is a donation
        (no sponsorship product inside)
        """
        res = super().action_invoice_paid()
        invoices = self._filter_invoice_to_thank()
        if invoices:
            invoices.generate_thank_you()
        return res

    def _compute_amount(self):
        """When invoice is open again, remove it from donation receipt."""
        payment_states = self.mapped("payment_state")
        super()._compute_amount()
        new_payment_states = self.mapped("payment_state")
        for i, state in enumerate(payment_states):
            invoice = self[i]
            if (
                state == "paid"
                and new_payment_states[i] != "paid"
                and invoice.communication_id.state == "pending"
            ):
                invoice.with_delay().cancel_thankyou_letter()

    def group_by_partner(self):
        """Returns a dict with {partner_id: invoices}"""
        res = dict()
        for partner in self.mapped("partner_id"):
            res[partner.id] = self.filtered(
                lambda i, partner=partner: i.partner_id == partner
            )
        return OrderedDict(
            sorted(
                res.items(),
                key=lambda t: sum(t[1].mapped("amount_total")),
                reverse=True,
            )
        )

    @api.model
    def thankyou_summary_cron(self):
        """
        Sends a summary each month of the donations
        :return: True
        """
        comm_obj = self.env["partner.communication.job"]
        first = datetime.today().replace(day=1)
        last_month = first - relativedelta(months=1)
        user_id = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("thankyou_letters.summary_user_id")
        )
        if user_id:
            partner = self.env["res.users"].browse(int(user_id)).mapped("partner_id")
            invoices = self.search(
                [
                    ("move_type", "=", "out_invoice"),
                    ("payment_state", "=", "paid"),
                    ("last_payment", ">=", last_month),
                    ("last_payment", "<", first),
                ]
            )
            config = self.env.ref("thankyou_letters.config_thankyou_summary")
            comm_obj.create(
                {
                    "config_id": config.id,
                    "partner_id": partner.id,
                    "object_ids": invoices.ids,
                }
            )
        return True

    def generate_thank_you(self):
        """
        Creates a thank you letter communication.
        """
        partners = self.mapped("partner_id").filtered(
            lambda p: p.thankyou_preference != "none"
        )
        for partner in partners.mapped("commercial_partner_id"):
            invoice_lines = self.mapped("invoice_line_ids").filtered(
                lambda line, p_partner=partner: line.partner_id == p_partner
            )
            if invoice_lines:
                invoice_lines.with_delay().generate_thank_you()

    def cancel_thankyou_letter(self):
        self.ensure_one()
        comm = self.communication_id
        object_ids = comm.object_ids or ""
        comm.unlink()
        # Check if the communication needs to be refreshed.
        for line in self.invoice_line_ids:
            object_ids = (
                object_ids.replace(str(line.id), "").replace(",,", "").strip(",")
            )
        if object_ids:
            # Refresh donation receipt
            remaining_lines = self.env["account.move.line"].browse(
                [int(i) for i in object_ids.split(",")]
            )
            remaining_lines.generate_thank_you()

    def _filter_invoice_to_thank(self):
        """
        Given a recordset of paid invoices, return only those that have
        to be thanked.
        :return: account.invoice recordset
        """
        return self.filtered(
            lambda i: i.move_type == "out_invoice"
            and not i.avoid_thankyou_letter
            and any(i.line_ids.mapped("product_id.requires_thankyou"))
            and (
                not i.communication_id
                or i.communication_id.state in ("call", "pending")
            )
        )
