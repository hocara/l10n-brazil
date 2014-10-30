# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
# Copyright (C) 2010  Renato Lima - Akretion                                  #
#                                                                             #
#This program is free software: you can redistribute it and/or modify         #
#it under the terms of the GNU Affero General Public License as published by  #
#the Free Software Foundation, either version 3 of the License, or            #
#(at your option) any later version.                                          #
#                                                                             #
#This program is distributed in the hope that it will be useful,              #
#but WITHOUT ANY WARRANTY; without even the implied warranty of               #
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                #
#GNU Affero General Public License for more details.                          #
#                                                                             #
#You should have received a copy of the GNU Affero General Public License     #
#along with this program.  If not, see <http://www.gnu.org/licenses/>.        #
###############################################################################

from openerp.osv import orm, fields
from openerp.tools.translate import _

def  calc_price_ratio(price_gross, amount_calc, amount_total):
    return price_gross * amount_calc / amount_total

class AccountInvoice(orm.Model):
    _inherit = 'account.invoice'
    _columns = {
        'carrier_id': fields.many2one(
            'delivery.carrier', 'Transportadora', readonly=True,
            states={'draft': [('readonly', False)]}),
        'vehicle_id': fields.many2one(
            'l10n_br_delivery.carrier.vehicle', u'Veículo', readonly=True,
            states={'draft': [('readonly', False)]}),
        'incoterm': fields.many2one(
            'stock.incoterms', 'Tipo do Frete', readonly=True,
            states={'draft': [('readonly', False)]},
            help="Incoterm which stands for 'International Commercial terms' "
            "implies its a series of sales terms which are used in the "
            "commercial transaction."),
    }

    def nfe_check(self, cr, uid, ids, context=None):
        result = super(AccountInvoice, self).nfe_check(cr, uid, ids, context)
        strErro = u''

        for inv in self.browse(cr, uid, ids, context=context):
            # Carrier
            if inv.carrier_id:

                if not inv.carrier_id.partner_id.legal_name:
                    strErro = u'Transportadora - Razão Social\n'

                if not inv.carrier_id.partner_id.cnpj_cpf:
                    strErro = 'Transportadora - CNPJ/CPF\n'

            # Carrier Vehicle
            if inv.vehicle_id:

                if not inv.vehicle_id.plate:
                    strErro = u'Transportadora / Veículo - Placa\n'

                if not inv.vehicle_id.state_id.code:
                    strErro = u'Transportadora / Veículo - UF da Placa\n'

                if not inv.vehicle_id.rntc_code:
                    strErro = u'Transportadora / Veículo - RNTC\n'

        if strErro:
            raise orm.except_orm(
                _('Error!'),
                _(u"Validação da Nota fiscal:\n '%s'") % (strErro))

        return result


class AccountInvoiceDeliveryValues(orm.Model):

    _name = 'account.invoice.delivery_values'

    _columns = {
       'amount_freight_value': fields.float('Frete'),
       'amount_insurance_value': fields.float('Seguro'),
       'amount_costs_value': fields.float('Outros Custos'),
    }

    def values_set(self, cr, uid, ids, context=None):

        invoice_pool = self.pool.get('account.invoice')
        invoice_line_pool = self.pool.get('account.invoice.line')
        delivery = self.browse(cr, uid, ids[0], context)

        if context.get('active_id', False):
            invoice_data = invoice_pool.read(cr, uid, context.get('active_id'), ['invoice_line', 'amount_gross'])

        invoice_pool.write(cr, uid, invoice_data['id'], {'amount_freight': delivery.amount_freight_value,
                                                         'amount_insurance': delivery.amount_insurance_value,
                                                         'amount_costs': delivery.amount_costs_value,
                                                         }, context=context)

        for line_id in invoice_data['invoice_line']:
            line = invoice_line_pool.browse(cr, uid, line_id, context)
            invoice_line_pool.write(cr, uid, line_id,
                                    {'freight_value': calc_price_ratio(
                                        line.price_gross, delivery.amount_freight_value, invoice_data['amount_gross']),
                                     'insurance_value': calc_price_ratio(
                                        line.price_gross, delivery.amount_insurance_value, invoice_data['amount_gross']),
                                     'other_costs_value': calc_price_ratio(
                                        line.price_gross, delivery.amount_costs_value, invoice_data['amount_gross']),
                                     }, context=context)


        return True

