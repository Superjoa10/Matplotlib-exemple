import matplotlib.pyplot as plt
import sqlite3
# TODO add to main agenda.py

SQLITE_FILE = 'Agenda_2023.db'

titles_fontdict = {'family': 'serif',
        'color':  'black',
        'weight': 'normal',
        'size': 20,
        }

# DB query data functions

def get_deals_and_payments_per_month(sqlite_location):
              deals_per_month = list()
              unmade_deals_per_month = list()
              payments_per_month = list()
              late_per_month = list()

              cursor = sqlite3.connect(sqlite_location)       
              for month in range(1, 13):
                     form_month = add_leading_zero(month)
                     month_name = get_month_name(month)
                     try:   
                            pay = cursor.execute(f"SELECT COUNT(*) FROM {month_name} WHERE pago = 1")
                            payments = pay.fetchone()[0]

                            late = cursor.execute(f"SELECT COUNT(*) FROM {month_name} WHERE pago = 2")
                            lates = late.fetchone()[0]

                            deal = cursor.execute(f"""
SELECT COUNT(*)
FROM {month_name}
WHERE strftime('%m', data) = '{form_month}' AND pago != 2;
""")
                            deals = deal.fetchone()[0]
                            #print(deals, month)

                            unmade_deal = cursor.execute(f"SELECT COUNT(*) FROM {month_name + '_unmade'}")
                            unmade_deals = unmade_deal.fetchone()[0]

                            deals_per_month.append(deals)
                            unmade_deals_per_month.append(unmade_deals)
                            payments_per_month.append(payments)
                            late_per_month.append(lates)

                            print(f'Successo! Mes {month_name} extraido com sucesso')
                     except:
                            print(f'Erro! mes {month_name} não possui table na database')

                     continue

              return deals_per_month, unmade_deals_per_month, payments_per_month, late_per_month, 

def calculate_averages(sqlite_location):
       payment_values = list()
       payment_sums = list()
       paid_payment_sums = list()
       cursor = sqlite3.connect(sqlite_location)

       for month in range(1, 13):
              form_month = add_leading_zero(month)
              month_name = get_month_name(month)
              try:  
                     # Query the database to get the average of all payment values for the specified year and month
                     avg_pay = cursor.execute(f"SELECT AVG(valor) FROM {month_name}")
                     payment_avg = avg_pay.fetchone()[0]
                     
                     # Query the database to get the sum of all deals payment values for the specified year and month
                     sum_pay = cursor.execute(f"SELECT SUM(valor) FROM {month_name} WHERE strftime('%m', data) = '{form_month}' AND pago != 2")
                     payment_sum = sum_pay.fetchone()[0]
                     
                     # Query the database to get the sum of paid payment values for the specified year and month
                     sum_pay_p = cursor.execute(f"SELECT SUM(valor) FROM {month_name} WHERE pago = 1")
                     paid_payment_sum = sum_pay_p.fetchone()[0]
                     
                     payment_sums.append(payment_sum)
                     paid_payment_sums.append(paid_payment_sum)
                     payment_values.append(payment_avg)

                     print(f'mes {month_name} extraido com sucesso')

              except:
                     print(f'mes {month_name} não possui table na database')
                     continue

       return payment_values, payment_sums, paid_payment_sums

def get_valid_month(sqlite_location):
       conn = sqlite3.connect(sqlite_location)  # Replace with your actual database name
       cursor = conn.cursor()

       # Get the list of tables in the database
       cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
       tables = cursor.fetchall()

       # Define a list of month names
       months = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

       # Initialize an empty list to store the valid month tables
       valid_month_tables = []

       # Iterate through the tables and check if they correspond to a month
       for table in tables:
              table_name = table[0]

              # Check if the table name corresponds to a month
              if table_name.capitalize() in months:
                     valid_month_tables.append(table_name[:3].capitalize())
       
       return valid_month_tables


# Graph functions

def plot_graph(year, deals_per_month, unmade_deals_per_month, payments_per_month, late_per_month, sqlite_location):
       months = get_valid_month(sqlite_location)

       plt.figure(figsize=(10, 6))

       plt.plot(months, deals_per_month, 'b.-', label='Acordos')
       plt.plot(months, unmade_deals_per_month, 'r.--', label='Acordos desfeitos')
       plt.plot(months, payments_per_month, 'g.-', label='Pagamentos')
       plt.plot(months, late_per_month, 'y.-', label='Atrasados')

       plt.xlabel('Mês', fontdict= titles_fontdict)
       plt.ylabel('Numero de Acordos', fontdict= titles_fontdict)
       plt.title(f'Acordos e Pagamentos em {year}', fontdict= titles_fontdict)
       plt.legend()
       plt.grid(True)

       for i, (deals, payments, unmade, late) in enumerate(zip(deals_per_month, payments_per_month, unmade_deals_per_month, late_per_month)):
              plt.text(months[i], deals, str(deals), ha='center', va='bottom', fontsize=10, color='darkblue')
              plt.text(months[i], payments, str(payments), ha='center', va='bottom', fontsize=10, color='darkgreen')

              plt.text(months[i], unmade, str(unmade), ha='center', va='bottom', fontsize=10, color='red')
              plt.text(months[i], late, str(late), ha='center', va='bottom', fontsize=10, color='orange')

       plt.show()

def plot_stem_graph(year, payment_values, payment_sums, paid_payment_sums, sqlite_location):
    months = get_valid_month(sqlite_location)

    plt.figure(figsize=(10, 6))
    plt.step(months, payment_values, 'ob-')
    plt.step(months, payment_sums, 'om-')
    plt.step(months, paid_payment_sums, 'og-')
    plt.xlabel('Mês', fontdict= titles_fontdict)
    plt.ylabel('Valor dos pagamentos', fontdict= titles_fontdict)
    plt.title(f'Valor aproximado dos pagamentos em {year}', fontdict= titles_fontdict)
    plt.legend(['Valor medio de acordo', 'Soma Acordos', 'Soma Acordos pagos'])
    plt.grid(True)

    for i, (payment_values, payment_sum, paid_payment_sum) in enumerate(zip(payment_values, payment_sums, paid_payment_sums)):
        plt.text(months[i], payment_values, f'{payment_values:.2f}', ha='center', va='bottom', fontsize=10, color='blue')
        plt.text(months[i], payment_sum, f'{payment_sum:.2f}', ha='center', va='bottom', fontsize=10, color='magenta')
        plt.text(months[i], paid_payment_sum, f'{paid_payment_sum:.2f}', ha='center', va='bottom', fontsize=10, color='green')

    plt.show()

def plot_month_data(month_name, sqlite_location): 
    conn = sqlite3.connect(sqlite_location) 
    cursor = conn.cursor()
    table_name = month_name.lower()

    cursor.execute(f"SELECT strftime('%d', data), COUNT(*) FROM {table_name} GROUP BY strftime('%d', data)")
    deals_per_day = cursor.fetchall()

    cursor.execute(f"SELECT strftime('%d', data), SUM(valor) FROM {table_name} GROUP BY strftime('%d', data)")
    payments_per_day = cursor.fetchall()

    conn.close()

    # Extract data for plotting
    days, deal_counts = zip(*deals_per_day)
    days, payment_sums = zip(*payments_per_day)

    # Ensure that all days have data points
    all_days = [str(i).zfill(2) for i in range(1, 32)]
    deal_counts_aligned = [deal_counts[days.index(day)] if day in days else 0 for day in all_days]
    payment_sums_aligned = [payment_sums[days.index(day)] if day in days else 0 for day in all_days]

    # Create the plot
    fig, ax1 = plt.subplots(figsize=(12, 8))

    ax1.plot(all_days, deal_counts_aligned, color='b', marker='.', label='Acordos por Dia')
    ax1.set_xlabel('Dia', fontdict= titles_fontdict)
    ax1.set_ylabel('Acordos', color='b')
    ax1.tick_params('y', colors='b')
    ax1.legend(loc='upper left')

    # Add labels to data points on the first plot (deal_counts_aligned)
    for i, (x, y) in enumerate(zip(all_days, deal_counts_aligned)):
       ax1.annotate(f'{y}', (x, y), textcoords="offset points", xytext=(0,10), ha='center', fontsize=10, color='blue')


    ax2 = ax1.twinx()
    ax2.plot(all_days, payment_sums_aligned, color='r', marker='o', label='Valor medio do acordo')
    ax2.set_ylabel('Payment Sum', color='r')
    ax2.tick_params('y', colors='r')
    ax2.legend(loc='upper right')
    
    for i, (x, y) in enumerate(zip(all_days, payment_sums_aligned)):
       ax2.annotate(f'R${y:.2f}', (x, y), textcoords="offset points", xytext=(0,10), ha='center', fontsize=10, color='red')

    plt.title(f"Acordos e valor medio de pagamento do mes de {month_name}", fontdict= titles_fontdict)
    plt.show()


# Helper

def get_month_name(month_number):
    months = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    
    if 1 <= month_number <= 12:
        return months[month_number - 1]
    else:
        raise TypeError

def add_leading_zero(number):
    number_str = str(number)
    if len(number_str) == 1:
        number_str = '0' + number_str
    return number_str


if __name__ == '__main__':
       year = 2023 #just for name

       deals_per_month, unmade_deals_per_month, payments_per_month, late_payed_per_month = get_deals_and_payments_per_month(SQLITE_FILE)
       plot_graph(year, deals_per_month, unmade_deals_per_month, payments_per_month, late_payed_per_month, SQLITE_FILE)

       payment_values, payment_sums, paid_payment_sums = calculate_averages(SQLITE_FILE)
       plot_stem_graph(year, payment_values, payment_sums, paid_payment_sums, SQLITE_FILE)

       plot_month_data('Janeiro', SQLITE_FILE)
