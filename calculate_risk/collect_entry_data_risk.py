# Charlightning
# Copyright (C) 2022 Sergio Andrés Estrada Vélez
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

class DataEntryRiskTable:
    def __init__(self):
        # Here you can initialize attributes or other necessary elements
        pass


    def get_risk_of_fire(self, selected_index):
        """
        Calculate the risk factor based on the selected index.

        :param selected_index: Index corresponding to the risk level.
            Options:
            0: Explosive - Possibility of explosion.
            1: High risk - Mech. & thermal effects. Significant fire or mech. damage, combustible roof.
            2: Ordinary risk - Mech. & thermal effects. Combustible building material.
            3: Low risk - Mech. & thermal effects. Modern reinforced concrete building.
            4: None - No mech. & thermal effects (all metal structure).

        :return: Risk factor (r_f) corresponding to the selected index.
        """
        options = [1, 0.1, 0.01, 0.001, 0]

        if 0 <= selected_index < len(options):
            r_f = options[selected_index]
            return r_f
        else:
            raise ValueError("Invalid selected index r_f.")

    def get_external_effectiveness (self, selected_index):
        """
        Calculate external structure screening effectiveness (Ks1).

        :param selected_index: Index for external structure type.
            Options:
            0: Poor - Brick, masonry, flammable material, timber or non-conducting - Ks1=1.0
            1: Average - Reinforced concrete or steel columns (spacing<=20m) - Ks1=0.2
            2: Good - All metal construction - Ks1=10^(-4)          

        :return: Ks1 corresponding to the selected index.
        """
        options = [1, 0.2, 10**(-4)]

        if 0 <= selected_index < len(options):
            Ks1 = options[selected_index]
            return Ks1
        else:
            raise ValueError("Invalid selected index Ks1.")

    def get_internal_effectiveness (self):
        """
        Screening effectiveness of zones internal to the structure. (Ks2).

        :param Ks2 : Fixed factor 1.0:

        :return: Ks2 corresponding to the selected index.
        """
        Ks2 = 1

        return Ks2


    def get_shock_prob_humans_animals(self):
        """
        Probability that lightning will cause a shock to animals or human beings
        inside and up to 3m outside of the structure due to dangerous step and 
        touch potentials. (PA).

        :param P_A : factor 1.0 (i.e. No protection measures adopted)

        :return: P_A corresponding to the selected index.
        """
        P_A = 1

        return P_A


    def get_lightning_strike_distance(self):
        """
        Distance from structure that a lightning strike to ground creates a magnetic field 
        sufficient to induce an over-voltage exceeding the impulse level of equipment 
        internal to the structure. (D_m).

        :param D_m : Fixed factor - 250m

        :return: D_m
        """
        D_m = 250

        return D_m

    def get_height_factor_surrounding(self, selected_index):
        """
        Calculate "Height factor for nearby object height" based on the selected index.

        Index:
        0: Lower height - Large area of structures or trees. e.g. CBD building or shed. - Factor: 0.25
        1: Similar height - Surrounded by smaller structures. e.g. tall building in urban area. - Factor: 0.5
        2: Isolated structure - No other structures within 3 times its height. e.g. rural area. - Factor: 1.0
        3: On a hilltop - Isolated structure on hilltop or knoll. e.g. communications site. - Factor: 2.0

        :param selected_index: Index corresponding to risk level.
        :return: Height factor (C_d) corresponding to selected index or None if index is invalid.
        """

        risk_factors = [0.25, 0.5, 1, 2]

        if 0 <= selected_index < len(risk_factors):
            C_d = risk_factors[selected_index]
            return C_d
        else:
            raise ValueError("Invalid selected index C_d.")


    def get_factor_line_density_C_e(self, selected_index):
        """
        Calculate "Height factor for nearby object height" based on the selected index.

        Service Line Density - Density factor relating to service drops.
        ///////////*
        Index:
        0: Urban high-rise buildings - 0
        1: Urban (i.e. Dense e.g. town or city) - 0.1
        2: Suburban (e.g. Large housing development or suburb) - 0.5
        3: Rural (i.e. Sparse e.g. farms) - 1

        :param selected_index: Index corresponding to risk level.
        :return: Density factor (C_e) corresponding to the selected index.
        """
        
        factor_line_service = [0, 0.1, 0.5, 1]

        if 0 <= selected_index < len(factor_line_service):
            C_e = factor_line_service[selected_index]
            return C_e
        else:
            raise ValueError("Invalid selected index C_e.")

    def get_number_thunder_T_d (self):
        """
        Td Number of thunder days per year
        """
        pass

    def get_annual_flash_density_DDT (self):
        """
        DDT Equivalent annual flash density
        """
        pass

    def get_internal_effectiveness_wiring_Ks3(self, selected_index):
        """
        Screening effectiveness of internal wiring type. (Ks3).

        Index:
        0: Screened (continuously) wiring - 0.1
        1: Unscreened wiring - 1.0

        :param Ks3 : Screening effectiveness of internal wiring type

        :return: Ks2 corresponding to the selected index.
        """
        factor_line_wiring = [0.1, 1]

        if 0 <= selected_index < len(factor_line_wiring):
            Ks3 = factor_line_wiring[selected_index]
            return Ks3
        else:
            raise ValueError("Invalid selected index Ks3.")






if __name__ == "__main__":
    instance = DataEntryRiskTable()
    print("r_f= " + str(instance.get_risk_of_fire(0)))
    print("Ks1= " + str(instance.get_external_effectiveness(0)))
    print("Ks3= " + str(instance.get_internal_effectiveness()))
    print("P_A= " + str(instance.get_shock_prob_humans_animals()))
    print("D_m= " + str(instance.get_lightning_strike_distance()))
    print("C_d= " + str(instance.get_height_factor_surrounding(0)))
    print("C_e= " + str(instance.get_factor_line_density_C_e(0)))

 # poner resumir nota y ponerla como comentarios de la  funcion calcular_Ks1 con el formato del comentario de la funcion get_risk_of_fire, tambien sujerir otro nombre para la funcion calcular_Ks1, todo en ingles  
 # nota= 
