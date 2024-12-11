# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, registry
from mercadolibre.src import mercadolibre as ml, mercadolibre_site as ml_site
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class MercadolibreConfiguration(models.Model):

    _inherit = 'mercadolibre.configuration'

    mercadolibre_current_login = fields.Boolean()
    mercadolibre_client_id = fields.Char('Mercadolibre client ID')
    mercadolibre_client_secret = fields.Char('Mercadolibre client secret')
    mercadolibre_access_token = fields.Char('Mercadolibre access token')
    mercadolibre_refresh_token = fields.Char('Mercadolibre refresh token')
    mercadolibre_redirect_uri = fields.Char('Mercadolibre redirect URI')
    mercadolibre_user_id = fields.Char('Mercadolibre user ID')
    mercadolibre_country_id = fields.Many2one(
        comodel_name='res.country',
        string='País',
        domain="[('mercadolibre_auth_url', '!=', False), ('mercadolibre_site_id', '!=', False)]"
    )

    def get_config_with_mercadolibre_current_login(self):
        return self.search([('mercadolibre_current_login', '=', True)], limit=1)

    def get_mercadolibre_lib(self):
        self.ensure_one()
        return ml.Mercadolibre(
            self.mercadolibre_client_id,
            self.mercadolibre_client_secret,
            self.mercadolibre_country_id.mercadolibre_auth_url,
            self.mercadolibre_access_token,
            self.mercadolibre_refresh_token
        )

    def get_mercadolibre_site_lib(self):
        self.ensure_one()
        return ml_site.MercadolibreSite(
            self.mercadolibre_client_id,
            self.mercadolibre_client_secret,
            self.mercadolibre_country_id.mercadolibre_auth_url,
            self.mercadolibre_access_token,
            self.mercadolibre_refresh_token,
            site=self.mercadolibre_country_id.mercadolibre_site_id
        )

    def update_token(self):
        """ Dejamos la función por compatibilidad """
        self.refresh_token()

    def update_all_tokens(self):
        for configuration in self.search([('mercadolibre_access_token', '!=', False)]):
            try:
                configuration.update_token()
            except Exception as e:
                _logger.info('No se pudo obtener el token de mercadolibre:\n{}'.format(e.args[0]))

    def log_in(self):
        if not (self.mercadolibre_client_id and self.mercadolibre_client_secret and self.mercadolibre_redirect_uri):
            raise ValidationError("Para poder iniciar sesión debe completar los datos de autenticación.")

    def log_out(self):
        self.write({
            'mercadolibre_access_token': None,
            'mercadolibre_refresh_token': None,
        })

    _sql_constraints = [(
        'client_user_unique',
        'unique (mercadolibre_client_id,mercadolibre_user_id)',
        'Ya existe una configuración con el Client ID y User ID ingresados'
    )]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
