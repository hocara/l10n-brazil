# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004 TINY SPRL. (http://tiny.be) All Rights Reserved.
#                    Fabien Pinckaers <fp@tiny.Be>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from osv import osv, fields
import pooler

class Cpf:
    def __init__( self ):
        pass

    def format( self, cpf ):
        return "%s.%s.%s-%s" % ( cpf[0:3], cpf[3:6], cpf[6:9], cpf[9:11] )

    def validar( self, cpf ):
        if not cpf.isdigit():
            """ Verifica se o CPF contem pontos e hifens """
            cpf = cpf.replace(".", "")
            cpf = cpf.replace("-", "")
        if len(cpf) < 11:
            """ Verifica se o CPF tem 11 digitos """
            return False
        if len(cpf) > 11:
            """ CPF tem que ter 11 digitos """
            return False
        selfcpf = [int(x) for x in cpf]
        cpf = selfcpf[:9]
        while len(cpf) < 11:
            r =  sum([(len(cpf)+1-i)*v for i,v in [(x,cpf[x]) for x in range(len(cpf))]]) % 11
            if r > 1:
                f = 11 - r
            else:
                f = 0
            cpf.append(f)
        return bool(cpf == selfcpf)

class Cnpj:
    def __init__( self ):
        pass
        
    def validar( self,cnpj ):
        # definindo algumas variaveis
        lista_validacao_um = [5,4,3,2,9,8,7,6,5,4 ,3,2]
        lista_validacao_dois = [6,5,4,3,2,9,8,7,6,5,4,3,2]
        
        # Limpando o cnpj
        cnpj = cnpj.replace("-","")
        cnpj = cnpj.replace(".","")
        cnpj = cnpj.replace("/","")
    
        # encontrando o digito de contorle
        verificadores = cnpj[-2:]
        
        # verificando o tamano do  cnpj
        if len( cnpj ) != 14:
            return False
        
        # calculando o primeiro digito
        soma = 0
        id = 0
        for numero in cnpj:
            try:
                lista_validacao_um[id]
            except:
                break
            soma += int(numero) * int(lista_validacao_um[id])
            id += 1
        
        soma = soma % 11
        if soma < 2:
            digito_um = 0
        else:
            digito_um = 11 - soma
        digito_um = str(digito_um) # convertendo para string para comparacao futura
        
        # calculando o segundo digito
        # somando as duas listas
        soma = 0
        id = 0
        
        # somando as duas listas
        for numero in cnpj:
            try:
                lista_validacao_dois[id]
            except:
                break
            soma += int(numero) * int(lista_validacao_dois[id])
            id += 1
        
        # definindo o digito
        soma = soma % 11
        if soma < 2:
            digito_dois = 0
        else:
            digito_dois = 11 - soma
        digito_dois = str(digito_dois)
    
        # returnig
        return bool(verificadores == digito_um + digito_dois )

    def format( self, cnpj ):
        return "%s.%s.%s/%s-%s" % ( cnpj[0:2], cnpj[2:5], cnpj[5:8], cnpj[8:12], cnpj[12:14] )


class res_partner(osv.osv):
    """Partner"""
    _name = 'res.partner'
    _inherit = 'res.partner'
    _columns = {
        'tipo_pessoa': fields.selection([('F', 'Física'), ('J', 'Jurídica')], 'Tipo de pessoa', required=True),
        'cpf_cnpj': fields.char('Cpf/CNPJ', size=15),
		'state' : fields.related ('address','state_id',type='many2one',relation='res.country.state', string='State'), 
        }
    def _check_cpf_cnpj(self, cr, uid, ids):
        for individuo in pooler.get_pool(cr.dbname).get('res.partner').read(cr, uid, ids, ['cpf_cnpj', 'tipo_pessoa']):
            nro_cpf_cnpj=individuo['cpf_cnpj']
            tipo_pessoa= individuo['tipo_pessoa']
            if tipo_pessoa == 'F':
                nr=Cpf()
                return nr.validar(nro_cpf_cnpj)
            else:
                if tipo_pessoa == 'J':
                    nr=Cnpj()
                    return nr.validar(nro_cpf_cnpj)
        return True
    _constraints = [(_check_cpf_cnpj, 'Erro: CPF/CNPJ Invalido', ['cpf_cnpj'])]

res_partner()

class res_partner_juridica(osv.osv):
    """Cadastro de pessoas juridica """
    _name = 'res.partner.juridica'
    _columns = {
        'name' : fields.many2one('res.partner','Razão social', required="1", domain=[('tipo_pessoa', '=', 'J')]),
		'city' : fields.related ('name','city',type='char',string='Cidade'), 
		'state' : fields.related ('name','state',type='many2one',relation='res.country.state', string='Estado'), 
		'country' : fields.related ('name','country',type='char',string='País'), 
        'fantasia' : fields.char('Nome Fantasia', size=25),
        'inscr_estadual': fields.char('Inscrição Estadual', size=20, required="1"),
        'inscr_municipal': fields.char('Inscrição Municipal', size=20),
        'data_fundacao': fields.date("Data da fundação"),
        'tipo_empresa': fields.selection([('I','Individual'), ('L','Limitada'), ('S','Sociedade Anônima'), ('P','Administração Pública')], 'Tipo de Empresa', required="1"),
     }            
res_partner_juridica()

class res_partner_fisica(osv.osv):
    """Cadastro de pessoas fisicas """
    _name = 'res.partner.fisica'
    _columns = {
        'name' : fields.many2one('res.partner','Nome', required="1", domain=[('tipo_pessoa', '=', 'F')]),
		'city' : fields.related ('name','city',type='char',string='Cidade'), 
		'state' : fields.related ('name','state',type='many2one',relation='res.country.state', string='Estado'), 
		'country' : fields.related ('name','country',type='char',string='País'), 
        'apelido': fields.char('Apelido', size=25),
        'identidade': fields.char('Identidade', size=20),
        'data_emissao_identidade': fields.date("Data de emissão"),
        'orgao_emissor_identidade': fields.char('Orgão emissor', size=6),
        'data_nascimento': fields.date("Data de Nascimento"),
        'estado_civil': fields.selection([('C', 'Casado'), ('S', 'Solteiro'), ('E', 'Desquitado'), ('D','Divorciado'), ('V','Viúvo')], 'Estado Civil'),
        'sexo': fields.selection([('M', 'Masculino'), ('F', 'Feminino')], 'Sexo', required="1"),
        'foto': fields.binary('Foto'),
     }            
res_partner_fisica()


