# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import SUPERUSER_ID, api


def migrate(cr, installed_version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env.cr.execute("CREATE temporary table mercadolibre_config_res_company_temp (config_id int, company_id int)")
    env.cr.execute(
        "INSERT INTO mercadolibre_config_res_company_temp (config_id, company_id)"
        "SELECT mercadolibre_configuration_id, id FROM res_company where mercadolibre_configuration_id is not null")
