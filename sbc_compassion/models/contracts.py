# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Compassion CH (http://www.compassion.ch)
#    Releasing children from poverty in Jesus' name
#    @author: Emanuel Cino <ecino@compassion.ch>
#
#    The licence is in the file __openerp__.py
#
##############################################################################

from openerp import api, fields, models


class Contracts(models.Model):
    """ Add correspondence information in contracts
    """

    _inherit = 'recurring.contract'

    ##########################################################################
    #                                 FIELDS                                 #
    ##########################################################################

    writing_language = fields.Many2one(
        'res.lang.compassion', related='reading_language',
        help='By now equals to reading language. Could be used in the future')
    child_letter_ids = fields.Many2many(
        'correspondence', string='Child letters',
        compute='_get_letters')
    sponsor_letter_ids = fields.Many2many(
        'correspondence', string='Sponsor letters',
        compute='_get_letters')
    nb_letters = fields.Integer(
        compute='_get_letters'
    )

    ##########################################################################
    #                             FIELDS METHODS                             #
    ##########################################################################
    def _get_letters(self):
        """ Retrieve correspondence of sponsorship contracts. """
        for sponsorship in self:
            letters_obj = self.env['correspondence']
            letters = letters_obj.search([
                ('sponsorship_id', '=', sponsorship.id)])
            sponsorship.child_letter_ids = letters.filtered(
                lambda l: l.direction == 'Beneficiary To Supporter')
            sponsorship.sponsor_letter_ids = letters.filtered(
                lambda l: l.direction == 'Supporter To Beneficiary')
            sponsorship.nb_letters = len(letters)

    ##########################################################################
    #                             VIEW CALLBACKS                             #
    ##########################################################################
    @api.onchange('correspondant_id', 'child_id')
    def onchange_relationship(self):
        """ Define the preferred reading language for the correspondent.
            1. Sponsor main language if child speaks that language
            2. Any language spoken by both sponsor and child other than
               English
            3. English
        """
        for sponsorship in self:
            if sponsorship.correspondant_id and sponsorship.child_id:
                sponsor = sponsorship.correspondant_id
                child_languages = sponsorship.child_id.field_office_id.\
                    spoken_language_ids
                sponsor_languages = sponsor.spoken_lang_ids
                lang_obj = self.env['res.lang.compassion']
                sponsor_main_lang = lang_obj.search([
                    ('lang_id.code', '=', sponsor.lang)])
                if sponsor_main_lang in child_languages:
                    sponsorship.reading_language = sponsor_main_lang
                else:
                    english = self.env.ref(
                        'child_compassion.lang_compassion_english')
                    common_langs = (child_languages &
                                    sponsor_languages) - english
                    if common_langs:
                        sponsorship.reading_language = common_langs[0]
                    else:
                        sponsorship.reading_language = english

    @api.multi
    def open_letters(self):
        letters = self.child_letter_ids | self.sponsor_letter_ids
        return {
            'name': letters._description,
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': letters._name,
            'context': self.with_context(
                group_by=False,
                search_default_correspondant_id=self.correspondant_id.id
            ).env.context,
            'target': 'current',
        }

    ##########################################################################
    #                            WORKFLOW METHODS                            #
    ##########################################################################
    @api.multi
    def contract_active(self):
        """ Send letters that were on hold. """
        super(Contracts, self).contract_active()
        for contract in self.filtered(
                lambda c: 'S' in c.type and not
                c.project_id.hold_s2b_letters):
            contract.sponsor_letter_ids.reactivate_letters(
                'Sponsorship activated')
