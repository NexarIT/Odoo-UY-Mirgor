# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import SUPERUSER_ID, api


def migrate(cr, installed_version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env.cr.execute(
        "UPDATE mercadolibre_configuration SET company_id = temp.company_id "
        "FROM mercadolibre_config_res_company_temp temp WHERE temp.config_id = mercadolibre_configuration.id"
    )
    env.cr.execute("""DROP TABLE mercadolibre_config_res_company_temp""")
