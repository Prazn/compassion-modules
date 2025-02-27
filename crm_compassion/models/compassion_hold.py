##############################################################################
#
#    Copyright (C) 2016-2018 Compassion CH (http://www.compassion.ch)
#    Releasing children from poverty in Jesus' name
#    @author: Emanuel Cino <ecino@compassion.ch>
#
#    The licence is in the file __manifest__.py
#
##############################################################################
from odoo import fields, models

from odoo.addons.child_compassion.models.compassion_hold import HoldType


class AbstractHold(models.AbstractModel):
    _inherit = "compassion.abstract.hold"

    campaign_id = fields.Many2one("utm.campaign", "Campaign", readonly=False)
    event_id = fields.Many2one("crm.event.compassion", "Event", readonly=False)

    def get_fields(self):
        _fields = super().get_fields()
        return _fields + ["campaign_id", "event_id"]

    def get_hold_values(self):
        """Get the field values of one record.
        :return: Dictionary of values for the fields
        """
        vals = super().get_hold_values()
        event = vals.get("event_id")
        if event:
            vals["event_id"] = event[0]
        campaign = vals.get("campaign_id")
        if campaign:
            vals["campaign_id"] = campaign[0]
        return vals


class CompassionHold(models.Model):
    _inherit = "compassion.hold"

    event_id = fields.Many2one(tracking=True, readonly=False)

    def get_origin(self):
        self.ensure_one()
        origin_obj = self.env["recurring.contract.origin"]
        origin_search = list()
        if self.type == HoldType.REINSTATEMENT_HOLD.value:
            origin_search.append(("name", "=", "Reinstatement"))
        elif self.channel == "event" and self.event_id:
            origin_search.append(("event_id", "=", self.event_id.id))
        elif self.channel == "ambassador" and self.ambassador:
            origin_search.append(("name", "=", self.ambassador.name))
        elif self.channel == "web":
            origin_search.append(("name", "=", "Internet"))
        if origin_search:
            return origin_obj.search(origin_search, limit=1)
        else:
            return origin_obj

    def reservation_to_hold(self, commkit_data):
        res_ids = super().reservation_to_hold(commkit_data)
        for hold in self.browse(res_ids):
            hold.event_id = hold.reservation_id.event_id
            hold.campaign_id = hold.reservation_id.campaign_id
        return res_ids


class ChildCompassion(models.Model):
    _inherit = "compassion.child"

    hold_event = fields.Many2one(related="hold_id.event_id", store=True, readonly=False)
    campaign_id = fields.Many2one(related="hold_id.campaign_id", readonly=False)


class Reservation(models.Model):
    _inherit = "compassion.reservation"

    event_id = fields.Many2one("crm.event.compassion", "Event", readonly=False)
    campaign_id = fields.Many2one("utm.campaign", "Campaign", readonly=False)
