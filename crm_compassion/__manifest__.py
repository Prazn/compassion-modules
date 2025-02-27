##############################################################################
#
#       ______ Releasing children from poverty      _
#      / ____/___  ____ ___  ____  ____ ___________(_)___  ____
#     / /   / __ \/ __ `__ \/ __ \/ __ `/ ___/ ___/ / __ \/ __ \
#    / /___/ /_/ / / / / / / /_/ / /_/ (__  |__  ) / /_/ / / / /
#    \____/\____/_/ /_/ /_/ .___/\__,_/____/____/_/\____/_/ /_/
#                        /_/
#                            in Jesus' name
#
#    Copyright (C) 2014-2023 Compassion CH (http://www.compassion.ch)
#    @author: Emanuel Cino <ecino@compassion.ch>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

# pylint: disable=C8101
{
    "name": "Compassion - Events",
    "summary": "Compassion Events and Opportunities",
    "version": "14.0.1.1.0",
    "development_status": "Beta",
    "category": "Customer Relationship Management",
    "website": "https://github.com/CompassionCH/compassion-modules",
    "author": "Compassion CH",
    "maintainers": ["ecino"],
    "license": "AGPL-3",
    "installable": True,
    "pre_init_hook": "pre_init_hook",
    "depends": [
        "base_location",  # OCA/partner_contact
        "web_widget_numeric_step",  # OCA/web
        "crm_phonecall",  # OCA/crm
        "sponsorship_compassion",  # compassion-modules
        "partner_contact_in_several_companies",  # oca_addons/partner-contact
        "mail_tracking_mass_mailing",  # OCA/social
        "base_automation",
        "thankyou_letters",
    ],
    "data": [
        "data/calendar_event_type.xml",
        "data/communication_config.xml",
        "data/demand_planning.xml",
        "security/crm_compassion_security.xml",
        "security/ir.model.access.csv",
        "static/src/xml/assets.xml",
        "views/account_invoice_line.xml",
        "views/calendar_event_view.xml",
        "views/calendar_view.xml",
        "views/contract_origin_view.xml",
        "views/crm_lead_view.xml",
        "views/demand_planning_settings.xml",
        "views/demand_planning.xml",
        "views/demand_weekly_revision.xml",
        "views/event_compassion_view.xml",
        "views/field_view.xml",
        "views/global_childpool_view.xml",
        "views/hold_view.xml",
        "views/interaction_resume_view.xml",
        "views/partner_log_interaction_wizard_view.xml",
        "views/partner_log_other_interaction_wizard_view.xml",
        "views/res_partner_view.xml",
        "views/sponsorship_view.xml",
    ],
    "qweb": ["static/src/xml/kanban_colors.xml"],
}
