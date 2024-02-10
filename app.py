from flask import Flask,render_template,request
import pandas as pd
import matplotlib.pyplot as plt
from graphWT import plot_graph_WT
from graphSC import plot_graph_SC
###

app = Flask(__name__)

# wind turbine inputs
input_data_wt = pd.read_csv("./data/input_wt.csv")
w_speed=pd.read_csv('./data/input_wt.csv', usecols=['Wind speed m/s'])
p_out=pd.read_csv('./data/input_wt.csv', usecols=['output(kW)'])

# transformer inputs
input_data_tr=pd.read_csv('./data/input_tr.csv')
secondary_voltage = pd.read_csv('./data/input_tr.csv',usecols=["secondary_voltage(Volts)"])
secondary_current = pd.read_csv('./data/input_tr.csv',usecols=["secondary_current(Amperes)"])
iron_losses = pd.read_csv('./data/input_tr.csv',usecols=["iron_losses"])
power_factor=pd.read_csv('./data/input_tr.csv',usecols=["power_factor"])

# insulator inputs
input_data_in = pd.read_csv('./data/input_in.csv')
n = pd.read_csv('./data/input_in.csv', usecols=['n'])
v_disc1 = pd.read_csv('./data/input_in.csv', usecols={'v_disc1'})

# solar cell inputs
input_data_sc = pd.read_csv('./data/input_sc.csv')
sdx = pd.read_csv('./data/input_sc.csv', usecols=['Voltage']).sort_values(by='Voltage', ascending=True)
sdy = pd.read_csv('./data/input_sc.csv', usecols=['Current'])
input_data_sc['Power'] = input_data_sc['Voltage'] * input_data_sc['Current']
input_data_sc.to_csv('./data/input_sc.csv', index=False)

## app.routes and functions for devices
@app.route('/wind_turbine',methods=['GET', 'POST'])
def rotor_rad():
    if request.method == 'POST':
        rotor_radius = float(request.form.get('rotorRadius'))
        
        def calculate_efficiency(power_out):
            efficiency = round((power_out / power_input) * 100, 2)
            eff_data.append(efficiency)

        eff_data = []
        k=len(input_data_wt)
        
        for i in range(0,k):
            wind_speed = w_speed.loc[i].item()
            power_out = p_out.loc[i].item()
            if wind_speed<3 or wind_speed>20:
                eff_data.append(0)
            else:
                power_input = 0.5*3.14*1.204*rotor_radius*wind_speed
                calculate_efficiency(power_out)
        
        dict = {'Efficiency': eff_data}
        df = pd.DataFrame(dict)
        df.to_csv('./data/output_wt.csv')

        plot_graph_WT()
        
    data = pd.read_csv('./data/output_wt.csv')
    data.reset_index()
    data.drop(columns="Unnamed: 0", inplace=True)
    data.index = data.index + 1
        
    return render_template('wind_turbine_index.html', tables=[data.to_html()], titles=[''])

@app.route('/transformer',methods=['GET', 'POST'])
def calc():
    if request.method == 'POST':
        np = float(request.form.get('np'))
        ns = float(request.form.get('ns'))
        winding_resistance = float(request.form.get('winding_resistance'))
        coupling_factor = float(request.form.get('coupling_factor'))

        n = np / ns

        k=len(input_data_tr)
        eff_data = []
        for i in range(0,k):  #calculating the copper loss
           sc=secondary_current.loc[i].item()
           iron=iron_losses.loc[i].item()
           sv=secondary_voltage.loc[i].item()
           pf=power_factor.loc[i].item()
           primary_current = sc * n * coupling_factor   #calculating primary current
           loss = ((primary_current ** 2) * winding_resistance) + ((sc ** 2) * winding_resistance)
          
           power_output = sc * sv * pf
           efficiency = round(((power_output) / (power_output+loss+iron)) * 100, 2)  # calculating the final efficiency
           eff_data.append(efficiency)

        dict = {'Efficiency': eff_data}
        df = pd.DataFrame(dict)
        df.to_csv('./data/output_tr.csv')

    data = pd.read_csv('./data/output_tr.csv')
    data.reset_index()
    data.drop(columns="Unnamed: 0", inplace=True)  # Reset index without adding a new column
    data.index = data.index + 1

    # Check if 'data' is not None before calling 'to_html'
    return render_template('transformer_index.html',tables=[data.to_html()], titles=[''])

@app.route('/insulator',methods=['GET', 'POST'])
def insulator():
    if request.method == 'POST':
        v_string = float(request.form.get('vString'))
        
        eff_data = []
            
        def efficiency(n_val,v_disc1_val):
            eff = round(v_string/(n_val*v_disc1_val)*100, 2)
            eff_data.append(eff)
            
        k = len(input_data_in)
        
        for i in range(0,k):
            num_of_turns = n.loc[i].item()
            volt_disc1 = v_disc1.loc[i].item()
            efficiency(num_of_turns,volt_disc1)
            
        dict = {'Efficiency': eff_data}
        df = pd.DataFrame(dict)
        df.to_csv('./data/output_in.csv')

    data = pd.read_csv('./data/output_in.csv')
    data.reset_index()
    data.drop(columns='Unnamed: 0', inplace=True)
    data.index = data.index + 1

    return render_template('insulator_index.html', tables=[data.to_html()], titles=[''])

@app.route('/solarcell',methods=['GET', 'POST'])
def solarcell():
    if request.method == 'POST':
        P_in = float(request.form.get('p_in'))

        k=len(input_data_sc)
        for i in range(0,k):
            if sdx.loc[i].item()==0.0:
                ssc=sdy.loc[i].item()
                break
        for i in range(0,k):
            if sdy.loc[i].item()==0.0:
                ocv = sdx.loc[i].item()
                break
        
        fill_factor = round((input_data_sc['Power'].max()/(ssc * ocv)), 2)
        efficiency_sc = round(((ssc * ocv * fill_factor) / P_in) * 100, 2)
        
        output_sc = []
        output_sc.append(efficiency_sc)
        
        dict = {'Efficiency': output_sc}
        df = pd.DataFrame(dict)
        df.to_csv('./data/output_sc.csv')
        
        plot_graph_SC()

    data = pd.read_csv('./data/output_sc.csv')
    data.reset_index()
    data.drop(columns='Unnamed: 0', inplace=True)
    data.index = data.index + 1
    
        
    return render_template('solar_cell.html', tables=[data.to_html()], titles=[''])

@app.route('/',methods=['GET', 'POST'])
def index():
    return render_template('index.html')

# final app.run command
if __name__ == '__main__':
    app.run(debug=True)