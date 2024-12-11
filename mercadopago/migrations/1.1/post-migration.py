# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import SUPERUSER_ID, api


def migrate(cr, installed_version):
    """ Seteo la redirect form del acquirer porque su data tiene noupdate, y debe estar seteado para que funcione """
    env = api.Environment(cr, SUPERUSER_ID, {})
    env.ref('mercadopago.payment_acquirer_mercadopago').redirect_form_view_id = env.ref('mercadopago.mercadopago_form')
