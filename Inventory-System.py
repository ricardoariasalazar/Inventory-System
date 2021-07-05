"""
Created by: Ricardo Arias 
Date of creation: April 5, 2020
Last modification: April 30, 2020
"""


def read_data():
    """
    Reads the data from the file AU_INV_START.txt and store it in start_dict
    """

    start_file = open('./data/AU_INV_START.txt', 'r')  # Variable that reads the file
    start_dict = {}  # Dictionary that will store the start information in AU_INV_START.txt
    c = 0  # Variable that counts the number of lines in the file

    for line in start_file:  # Loop that reads each line of the .txt file and store it in start_dict
        if c == 0:  # First line of the file
            start_dict['start_year'] = int(line.strip())
        elif c == 1:  # Second line of the file
            start_dict['start_stock'] = int(line.strip())
        elif c == 2:  # Third line of the file
            start_dict['start_revenue'] = int(line.strip())
        else:  # More information stored in the file are not useful
            break

        c += 1  # Add 1 to c and keep counting lines in the file

    return start_dict  # Output: Dictionary with the start values stored in it


def cal_stock_revenue(dictionary):
    """
    Calculate total stock remaining and total revenue of a single year's cycle
    """
    # Input values
    NO_YEAR_SIM = int(input("How many years you want to simulate? (3 Default Value): ") or "3")
    PER_DEF = int(input("What is the percentage (%) of defective items per month? (5 Default Value): ") or "5")
    CRIS_RECUR_FREQUENCY = int(input("What is the frequency of the Financial Crisis? (9 Default Value): ") or "9")
    # default value taken from https://stackoverflow.com/questions/22402548/default-values-on-empty-user-input

    # Initial values of the simulation
    stock = dictionary['start_stock']  # Initial stock
    revenue = dictionary['start_revenue']  # Initial revenue
    start_year = int(str(dictionary['start_year'])[:4])  # Initial year of simulation

    # Initial month of simulation
    if str(dictionary['start_year'])[4] == '0':
        start_month = int(str(dictionary['start_year'])[5])
    else:
        start_month = int(str(dictionary['start_year'])[4:6])

    # Initial day of simulation
    if str(dictionary['start_year'])[6] == '0':
        start_day = int(str(dictionary['start_year'])[7])
    else:
        start_day = int(str(dictionary['start_year'])[6:])

    start_date = str(dictionary['start_year'])[4:] # Initial date of simulation
    start_simulation = False  # Initial status of simulation
    distribution = round(36 / 1.35)  # 36 Cantilever Umbrellas per day were distributed in January 1, 2000 (peak season)
    rrp = float(format((705 / 1.2), '.2f'))  # $705 AUD was the RRP of each umbrella in January 1, 2000 (peak season)
    # format(number, '.2f') taken from https://stackoverflow.com/questions/455612/limiting-floats-to-two-decimal-points

    # Dictionary where all the output values are going to be stored
    end_dict = {'end_year': str(start_year + NO_YEAR_SIM) + start_date, 'end_stock': '', 'end_revenue': ''}
    end_rrp = 0

    # If that defines the start date of the simulation (One day after of the date in the input).
    # If the date given is the last day of some month the simulation has to start the first day of the next month
    # If the date given is the last day of the yaer the simulation has to start on Jan 1st of the next year
    if start_month in (1, 3, 5, 7, 8, 10) and start_day == 31:
        start_day = 1
        start_month += 1
    if start_month == 12 and start_day == 31:
        start_day = 1
        start_month = 1
        start_year = int(str(dictionary['start_year'])[:4]) + 1
    elif start_month in (4, 6, 9, 11) and start_day == 30:
        start_day = 1
        start_month += 1
    elif start_year % 4 == 0 and start_month == 2 and start_day == 29:
        start_day = 1
        start_month += 1
    elif start_year % 4 != 0 and start_month == 2 and start_day == 28:
        start_day = 1
        start_month += 1
    else:
        start_day += 1

    # Minimum stock allowed
    min_stock = 400  # If the inventory stock is 400, the firm will restock 600 umbrellas

    # Season values
    dist_peakseason = 0.35  # The distribution in peak season increases in 35%
    rrp_peakseason = 0.2  # RRP in peak season increases in 20%

    # New financial year (It starts in July 1 of each year)
    dist_newfinancialyear = 0.1  # The distribution increases in 10% each new financial year (rounded up)
    rrp_newfinancialyear = 0.05  # The RRP increases in 5% each new financial year (Due to inflation)

    # Global financial crisis happens every 9 years and lasts 3 years including the year that happens. The crisis starts
    # on January 1 of the 9th year and will end on December 31 of 2 years later (3 years in total)
    dist_globfincris1 = 0.2  # The number of umbrellas distributed drop by 20% in the first year of global crisis
    dist_globfincris2 = 0.1  # The number of umbrellas distributed drop by 10% in the second year of global crisis
    dist_globfincris3 = 0.05  # The number of umbrellas distributed drop by 5% in the third year of global crisis
    rrp_globfincris1 = 0.1  # The company increases by 10% RRP in the first year of global crisis
    rrp_globfincris2 = 0.05  # The company increases by 5% RRP in the second year of global crisis
    rrp_globfincris3 = 0.03  # The company increases by 3% RRP in the third year of global crisis

    # Defective umbrellas returned
    dist_defective = PER_DEF / 100  # Input of the user
    rrp_defective = 0.8  # The defective umbrellas are refurbished and redistributed the next month at 80% of RRP

    # Variables created by me in order to make possible the loops and if statements
    count_years = 0  # Counter of the years that have been no global financial crisis
    count_crisisyears = 0  # Counter of the years that have been a global financial crisis
    is_peakseason = True  # As the simulation always starts in January 1st of 2020 it is true that it is peak season

    # Two of the most important variables of the simulation because it will store the value of all of the events that
    # are about to happen and it will multiplicate the initial value (January 1, 2000) to get the final value
    dist_multiplier = 1  # Multiplier of the initial value to get the final value of distribution
    rrp_multiplier = 1  # Multiplier of the initial value to get the final value of RRP
    dist_simyears = []  # Empty list that will store the dist_multiplier of the years of simulation
    rrp_simyears = []  # Empty list that will store the rrp_multiplier of the years of simulation

    # Months and years of the simulation will be stored in these lists. While the status of the simulation is True
    sim_months = []
    sim_years = []

    # Loops that define the calendar from 2000 to the year that the user wants to simulates
    for year in range(2000, (start_year + 1 + NO_YEAR_SIM)):

        # If that recreates the global financial crisis (every 9 years)
        if count_years >= CRIS_RECUR_FREQUENCY:
            count_crisisyears += 1  # Start to count the years of the global financial crisis
            if count_crisisyears == 1:  # If it is the first year of global financial crisis
                dist_multiplier *= (1 - dist_globfincris1)  # The distribution will drop 20%
                rrp_multiplier *= (1 + rrp_globfincris1)  # The RRP will increase 10%
            elif count_crisisyears == 2:  # If it is the second year of global financial crisis
                dist_multiplier *= (1 - dist_globfincris2)  # The distribution will drop 10%
                rrp_multiplier *= (1 + rrp_globfincris2)  # The RRP will increase 5%
            else:  # If it is the third year of global financial crisis
                dist_multiplier *= (1 - dist_globfincris3)  # The distribution will drop 5%
                rrp_multiplier *= (1 + rrp_globfincris3)  # The RRP will increase 3%
                count_years = 0  # After 3 years of crisis the counter return to 0
                count_crisisyears = 0  # After 3 years of crisis the counter return to 0

        # In this first for loop I will define the value of multipliers and store it in a list
        for month in range(1, 13):  # Loop of months. From 1 (January) to 12 (December)

            # If that recreates the peak season (From November to February)
            if month in (11, 12, 1, 2):  # If the month is November(11) - February(2) it is peak season
                if is_peakseason:
                    dist_multiplier *= (1 + dist_peakseason)  # Increase the multiplier 35% because it is peak season
                    rrp_multiplier *= (1 + rrp_peakseason)  # Increase the multiplier 20% because it is peak season
                    is_peakseason = False  # It is no peak season any more a soon as we already increase the 35%
            else:  # If the month is March (3) - October (10) it is not peak season
                if not is_peakseason:
                    dist_multiplier /= (1 + dist_peakseason)  # Decrease 35% because it is not peak season
                    rrp_multiplier /= (1 + rrp_peakseason)  # Decrease 20% because it is not peak season
                    is_peakseason = True  # It is peak season again a soon as we already decrease the 35%

            # If that recreates the new financial year (Happens in July 1st of each year)
            if month == 7:  # If the month is July (7)
                dist_multiplier *= (1 + dist_newfinancialyear)  # Increase 10% because it is new financial year
                rrp_multiplier *= (1 + rrp_newfinancialyear)  # Increase 5% because it iis new financial year

            # If that says when the simulation has started
            if year == start_year and month == start_month:  # Month and year of the input
                start_simulation = True  # The simulation has started

            # If that says when the simulation stops
            if year == (start_year + NO_YEAR_SIM) and month == (start_month + 1):
                start_simulation = False

            # If that saves the values of the multipliers while the simulation has started
            if start_simulation:
                dist_simyears.append(dist_multiplier)
                rrp_simyears.append(rrp_multiplier)
                sim_months.append(month)
                sim_years.append(year)

        count_years += 1  # Counter of years of global financial crisis

    # In this second for loop I will use the multiplier values to find the stock and revenue of the simulated year
    count_sim = 0  # Counter that identifies the first and the last day of the month, based on the date of the input
    for month in sim_months:
        count_sim += 1  # Counts the number of months of the simulation

        if month in (1, 3, 5, 7, 8, 10, 12):  # If that defines the months that have 31 days

            # If that identifies the starting and last day of the month based on the date of the input .txt
            if count_sim == 1:
                first_day = start_day
                last_day = 31
            elif count_sim == len(sim_months):
                first_day = 1
                last_day = start_day - 1
            else:
                first_day = 1
                last_day = 31

            for day in range(first_day, last_day + 1):
                end_dist = round(distribution * dist_simyears[count_sim - 1])  # Distribution of the day
                end_rrp = float(format((rrp * rrp_simyears[count_sim - 1]), '.2f'))  # RRP of the day
                revenue += (end_dist * end_rrp)  # Revenue of the day

                # If that ensures that the inventory stock is not below 400
                if stock > min_stock:
                    stock -= end_dist  # Every umbrella distributed is one umbrella out of the stock
                else:
                    stock += 600  # Restock 600 umbrellas when the inventory is below 400
                    stock -= end_dist  # Every umbrella distributed is one umbrella out of the stock

            # Defective Items (The company lose 20% of the price of each umbrellas because they resell price is 80%)
            if month == 1:
                revenue -= round(distribution * dist_simyears[count_sim - 1] * 31 * dist_defective) * end_rrp * (1 - rrp_defective)
            else:
                revenue -= round(distribution * dist_simyears[count_sim - 2] * 31 * dist_defective) * end_rrp * (1 - rrp_defective)

        elif month in (4, 6, 9, 11):  # If that defines the months that have 30 days

            # If that identifies the starting and last day of the month based on the date of the input .txt
            if count_sim == 1:
                first_day = start_day
                last_day = 30
            elif count_sim == len(sim_months):
                first_day = 1
                last_day = start_day - 1
            else:
                first_day = 1
                last_day = 30

            for day in range(first_day, last_day + 1):
                end_dist = round(distribution * dist_simyears[count_sim - 1])  # Distribution of the day
                end_rrp = float(format((rrp * rrp_simyears[count_sim - 1]), '.2f'))  # RRP of the day
                revenue += (end_dist * end_rrp)  # Revenue of the day

                # If that ensures that the inventory stock is not below 400
                if stock > min_stock:
                    stock -= end_dist  # Every umbrella distributed is one umbrella out of the stock
                else:
                    stock += 600  # Restock 600 umbrellas when the inventory is below 400
                    stock -= end_dist  # Every umbrella distributed is one umbrella out of the stockk

            # Defective Items (The company lose 20% of the price of each umbrellas because they resell price is 80%)
            revenue -= round(distribution * dist_simyears[count_sim - 2] * 30 * dist_defective) * end_rrp * (1 - rrp_defective)

        else:  # If that defines the number of days of february
            if (sim_years[count_sim - 1] % 4) == 0:  # If this condition is true it would be a leap year (29 days of Feb)

                # If that identifies the starting and last day of the month based on the date of the input .txt
                if count_sim == 1:
                    first_day = start_day
                    last_day = 29
                elif count_sim == len(sim_months):
                    first_day = 1
                    last_day = start_day - 1
                else:
                    first_day = 1
                    last_day = 29

                for day in range(first_day, last_day + 1):
                    end_dist = round(distribution * dist_simyears[count_sim - 1])  # Distribution of the day
                    end_rrp = float(format((rrp * rrp_simyears[count_sim - 1]), '.2f'))  # RRP of the day
                    revenue += (end_dist * end_rrp)  # Revenue of the day

                    # If that ensures that the inventory stock is not below 400
                    if stock > min_stock:
                        stock -= end_dist  # Every umbrella distributed is one umbrella out of the stock
                    else:
                        stock += 600  # Restock 600 umbrellas when the inventory is below 400
                        stock -= end_dist  # Every umbrella distributed is one umbrella out of the stock

                # Defective Items (The company lose 20% of the price of each umbrellas because they resell price is 80%)
                revenue -= round(distribution * dist_simyears[count_sim - 2] * 29 * dist_defective) * end_rrp * (1 - rrp_defective)

            else:  # If this condition is true it would be a normal year (28 days of Feb)

                # If that identifies the starting and last day of the month based on the date of the input .txt
                if count_sim == 1:
                    first_day = start_day
                    last_day = 28
                elif count_sim == len(sim_months):
                    first_day = 1
                    last_day = start_day - 1
                else:
                    first_day = 1
                    last_day = 28

                for day in range(first_day, last_day + 1):
                    end_dist = round(distribution * dist_simyears[count_sim - 1])  # Distribution of the day
                    end_rrp = float(format((rrp * rrp_simyears[count_sim - 1]), '.2f'))  # RRP of the day
                    revenue += (end_dist * end_rrp)  # Revenue of the day

                    # If that ensures that the inventory stock is not below 400
                    if stock > min_stock:
                        stock -= end_dist  # Every umbrella distributed is one umbrella out of the stock
                    else:
                        stock += 600  # Restock 600 umbrellas when the inventory is below 400
                        stock -= end_dist  # Every umbrella distributed is one umbrella out of the stock

                # Defective Items (The company lose 20% of the price of each umbrellas because they resell price is 80%)
                revenue -= round(distribution * dist_simyears[count_sim - 2] * 28 * dist_defective) * end_rrp * (1 - rrp_defective)

    # The final stock is the one calculated above plus the defective items returned in december of this year
    end_dict['end_stock'] = stock + int(distribution * dist_simyears[-1] * 31 * dist_defective)
    end_dict['end_revenue'] = "${:,.2f}".format(revenue)
    # "${:,.2f}".format(number) taken from https://kite.com/python/answers/how-to-format-currency-in-python

    return end_dict

def write_data(dictionary):
    """
    Writes the data that come from the simulation and store it in a file called AU_INV_END.txt
    """

    end_file = open('./output/AU_INV_END.txt', 'w')  # Variable that writes the file

    for line in range (3):  # Loop that writes each line of the directory in a .txt file
        if line == 0:  # First line of the file
            end_file.write(str(dictionary['end_year']))
            end_file.write("\n")
        elif line == 1:  # Second line of the file
            end_file.write(str(dictionary['end_stock']))
            end_file.write("\n")
        else:  # Third line of the file
            end_file.write(str(dictionary['end_revenue']))

    return end_file  # Output: .txt file with the end values stored in it

data = read_data()
revenue = cal_stock_revenue(data)
output = write_data(revenue)
