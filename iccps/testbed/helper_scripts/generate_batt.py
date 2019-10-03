house_num = ['b1m1','b1m2','b1m3','b1m4','b1m5','b1m6','b1m7','b1m8','b1m9','b1m10','b2m1','b2m2','b2m3','b2m4','b2m5','b2m6','b2m7','b2m8','b2m9','b2m10','b3m1','b3m2','b3m3','b3m4','b3m5','b3m6','b3m7','b3m8','b3m9','b3m10']
phases = ['BS','CS','CS','BS','BS','AS','BS','BS','AS','AS','CS','AS','AS','AS','CS','AS','AS','CS','CS','BS','BS','CS','BS','BS','BS','AS','AS','CS','AS','CS']
meter_name = ['branch_1_meter_1','branch_1_meter_2','branch_1_meter_3','branch_1_meter_4','branch_1_meter_5','branch_1_meter_6','branch_1_meter_7','branch_1_meter_8','branch_1_meter_9','branch_1_meter_10', \
'branch_2_meter_1','branch_2_meter_2','branch_2_meter_3','branch_2_meter_4','branch_2_meter_5','branch_2_meter_6','branch_2_meter_7','branch_2_meter_8','branch_2_meter_9','branch_2_meter_10', \
'branch_3_meter_1','branch_3_meter_2','branch_3_meter_3','branch_3_meter_4','branch_3_meter_5','branch_3_meter_6','branch_3_meter_7','branch_3_meter_8','branch_3_meter_9','branch_3_meter_10',]

ofile = open("inverters.txt",'w')
for i in range(30):
    if(i%4 != 0):
        ostring ="""//{2}
object transformer {{
     name {1}_house_trans;
     phases {0};
     from {2};
     to {1}_house_node;
     configuration house_transformer;
}}

object triplex_node {{
  name {1}_house_node;
  phases {0};
  nominal_voltage 120;
}}

object triplex_line {{
	groupid F1_Triplex_Line;
	phases {0};
	from {1}_house_node;
	to {1}_batt_meter;
	length 10 ft;
	configuration TLCFG;
}}

object triplex_line {{
	groupid F1_Triplex_Line;
	phases {0};
	from {1}_house_node;
	to {1}_solar_meter;
	length 10 ft;
	configuration TLCFG;
}}

object triplex_meter {{
  name {1}_solar_meter;
	phases {0};
	nominal_voltage 120;
	groupid inverter_meter;

	object inverter {{
		name {1}_solar_inv;
		phases {0};
		inverter_type FOUR_QUADRANT;
		power_factor 1;
		use_multipoint_efficiency TRUE;
		inverter_manufacturer XANTREX;
		maximum_dc_power 5000;
		four_quadrant_control_mode CONSTANT_PF;
		generator_status ONLINE;
		rated_power 5000;
		inverter_efficiency 0.90;

		object solar {{
			name {1}_solar;
			generator_mode SUPPLY_DRIVEN;
			generator_status ONLINE;
			panel_type SINGLE_CRYSTAL_SILICON;
			orientation FIXED_AXIS;
			rated_power 5000;
		}};
	}};
}}

object triplex_meter {{
  name {1}_batt_meter;
	phases {0};
	nominal_voltage 120;
	groupid inverter_meter;

	object inverter {{
		name {1}_batt_inv;
		phases {0};
		inverter_type FOUR_QUADRANT;
		power_factor 1;
		use_multipoint_efficiency TRUE;
		inverter_manufacturer XANTREX;
		four_quadrant_control_mode CONSTANT_PQ;
		generator_status ONLINE;
		rated_power 5000;
		inverter_efficiency 0.90;
		P_Out 0; //VA

		object battery {{
			name {1}_batt;
			parent {1}_batt_inv;
			use_internal_battery_model TRUE;
			battery_type LI_ION;
			rated_power 5000;
			nominal_voltage 120;
			battery_capacity 14 kWh;
			round_trip_efficiency 0.9;
			state_of_charge 0;
			generator_mode SUPPLY_DRIVEN;
		}};
	}};
}}\n\n""".format(phases[i], house_num[i], meter_name[i]);
        ofile.write(ostring)
    else:
        ostring ="""//{2}
object transformer {{
     name {1}_house_trans;
     phases {0};
     from {2};
     to {1}_house_node;
     configuration house_transformer;
}}

object triplex_node {{
  name {1}_house_node;
  phases {0};
  nominal_voltage 120;
}}

object house {{
	name {1}_house;
	parent {1}_house_node;
	schedule_skew 577;
	Rroof 17.618;
	Rwall 6.872;
	Rfloor 4.818;
	Rdoors 3;
	Rwindows 1.315;
	airchange_per_hour 1.288;
	hvac_power_factor 0.97;
	cooling_system_type ELECTRIC;
	heating_system_type GAS;
	fan_type ONE_SPEED;
	hvac_breaker_rating 200;
	total_thermal_mass_per_floor_area 4.311;
	motor_efficiency AVERAGE;
	motor_model BASIC;
	cooling_COP 2.502;
	floor_area 637.886;
	number_of_doors 1;
	air_temperature 68.886;
	mass_temperature 68.886;
	heating_setpoint heating5*1.043+1.41;
object ZIPload {{
	schedule_skew 577;
	heat_fraction 0.889;
	base_power LIGHTS*1.7284;
	power_pf 0;
	power_fraction 0;
	current_pf 0;
	current_fraction 0;
	impedance_pf 1;
	impedance_fraction 1;
}};
object ZIPload {{
	schedule_skew 577;
	heat_fraction 0.732;
	base_power CLOTHESWASHER*0.9135;
	power_pf 0.97;
	power_fraction 1;
	current_pf 0.97;
	current_fraction 0;
	impedance_pf 0.97;
	impedance_fraction 0;
}};
object ZIPload {{
	schedule_skew 577;
	heat_fraction 0.853;
	base_power REFRIGERATOR*0.8837;
	power_pf 0.97;
	power_fraction 1;
	current_pf 0.97;
	current_fraction 0;
	impedance_pf 0.97;
	impedance_fraction 0;
}};
object ZIPload {{
	schedule_skew 577;
	heat_fraction 0.875;
	base_power DRYER*0.5453;
	power_pf 0.9;
	power_fraction 0.1;
	current_pf 0.9;
	current_fraction 0.1;
	impedance_pf 1;
	impedance_fraction 0.8;
}};
object ZIPload {{
	schedule_skew 577;
	heat_fraction 0.76;
	base_power RANGE*0.6705;
	power_pf 0;
	power_fraction 0;
	current_pf 0;
	current_fraction 0;
	impedance_pf 1;
	impedance_fraction 1;
}};
object ZIPload {{
	schedule_skew 577;
	heat_fraction 0.951;
	base_power MICROWAVE*0.7977;
	power_pf 0.97;
	power_fraction 1;
	current_pf 0.97;
	current_fraction 0;
	impedance_pf 0.97;
	impedance_fraction 0;
}};
}}\n\n""".format(phases[i], house_num[i], meter_name[i],i);
        ofile.write(ostring)


ofile.close()
