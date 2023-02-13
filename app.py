import pandas as pd
import plotly.express as px
import dash
# import dash_html_components as html
from dash import html
from dash import dash_table
# import dash_core_components as dcc
from dash import dcc
from dash.dependencies import Input, Output


# Step 1: Data cleaning
#########################################################################################


# Load your commodity data into a pandas DataFrame
df = pd.read_csv('D:\Ablaze\commodity_data.csv')

# Cleaning the data i.e replacing null values with zero
df.fillna(value=0, inplace=True)


# Replacing '-' with 0
df['Production'] = df['Production'].replace('-', '', regex=True)

# converting the data type of supply column to integer
df['Production'] = pd.to_numeric(df['Production'])



# Step 2: Dashboard design
###################################################################################################

# Get the total production amount
total_production = df["Production"].sum()

df["Percentage"] = df["Production"] / total_production * 100



# Create a list of unique regions and commodities
regions = df['Region'].unique()
commodities = df['Commodity'].unique()

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the dashboard
app.layout = html.Div([
   
    html.Div([
        html.H2("Commodities Dashboard"),
        ], style={"text-align": "center"}),
    html.Div([
        html.Div([
            html.P("Select a region: "),
            dcc.Dropdown(
                id="region_dropdown",
                options=[{"label": r, "value": r} for r in regions],
                value="All"
            ),
        ], style={"width": "20%", "display": "inline-block","padding-left":"20px"}),
        html.Div([
            html.P("Select a commodity: "),
            dcc.Dropdown(
                id="commodity_dropdown",
                options=[{"label": c, "value": c} for c in commodities],
                value="All"
            ),
    ], style={"width": "20%", "display": "inline-block","padding-left":"20px"}),
    ]),
  
#section one
   
   html.Div([
        dcc.Graph(id='commodity-production-graph')
    ], style={"width": "80%", "display": "inline-block","margin-left":"60px"}),


   html.Div([
        dcc.Graph(id="region_production_pie"),
    ], style={"width": "100%", "display": "inline-block"}),
 ##Section 2
     html.Div([
        dcc.Graph(id='production-bar-graph')
    ], style={"width": "59%", "display": "inline-block"}),
  
       html.Div([
        dcc.Graph(id='pie_chart')
    ], style={"width": "39%", "display": "inline-block"}),

##section 3
 




 
])




# Define the callback functions


##################### Section One 
# 1.1 Total Production amount

# Define the callback for updating the graph
@app.callback(
    Output('commodity-production-graph', 'figure'),
    [Input('region_dropdown', 'value')]
)
def update_commodity_production_graph(selected_region):
    total_production_amount=df['Production'].sum()
    if selected_region == "All":
        filtered_df = df.sort_values(by='Production', ascending=False)
    else:
        filtered_df = df[df["Region"] == selected_region].sort_values(by='Production', ascending=False)
        total_production_amount=filtered_df['Production'].sum()
    fig = px.bar(filtered_df, x='Commodity', y='Production', color='Commodity')
    # fig.update_layout(plot_bgcolor="#57be94")
    fig.add_annotation(
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        text="Total Production: {:,}".format(total_production_amount),
        align="center",
        font_size=16,
        xanchor="left",
        yanchor="bottom",
        showarrow=False
    )
    
    return fig



# 1.2 Total production ratio or percentage of regions








################ Section Two

# 2.1 Sub-region production bar for selected region

@app.callback(
    dash.dependencies.Output('production-bar-graph', 'figure'),
    [dash.dependencies.Input('commodity_dropdown', 'value'),
     dash.dependencies.Input('region_dropdown', 'value')])
def update_production_bar_graph(commodity, region):
    if region == "All" and commodity=="All" :
         df_filtered = df.sort_values(by='Production', ascending=False)
    elif region == "All" and not commodity == "All":
         df_filtered = df[(df['Commodity'] == commodity)].sort_values(by='Production', ascending=False)
    elif commodity == "All" and not region == "All":
         df_filtered = df[(df['Region'] == region)].sort_values(by='Production', ascending=False)
    else:
        df_filtered = df[(df['Commodity'] == commodity) & (df['Region'] == region)].sort_values(by='Production', ascending=False)
    fig = px.bar(df_filtered, x='Sub-Region', y='Production', color='Commodity',color_continuous_scale='Blues')
    fig.update_layout(title={
        'text': "Sub-Regions Production of " + region + " for " + commodity + " commodities",
        'font': {'size': 18}
    })
    return fig




# 2.2 Sub region production pie chart for selected region

@app.callback(
    Output(component_id='pie_chart', component_property='figure'),
    [dash.dependencies.Input('commodity_dropdown', 'value'),
     dash.dependencies.Input('region_dropdown', 'value')])
def update_pie_chart(selected_commodity,selected_region):
    if selected_region == "All" and selected_commodity=='All':
        df_filtered=df
    elif selected_region == "All" and not selected_commodity=='All':
        df_filtered = df[df['Commodity'] == selected_commodity]
    elif selected_commodity == "All" and not selected_region=='All':
        df_filtered = df[df['Region'] == selected_region]

    else:
        df_filtered = df[(df['Region'] == selected_region) & (df['Commodity'] == selected_commodity)].sort_values(by='Production', ascending=False)
    total_production = df_filtered['Production'].sum()
    df_pie = df_filtered.groupby('Sub-Region').sum().reset_index()
    df_pie['percentage'] = df_pie['Production'] / total_production * 100
    df_pie = df_pie.sort_values(by='percentage', ascending=False)
    df_pie = df_pie.head(10)

    fig = px.pie(df_pie, values='Production', names='Sub-Region')
    fig.update_layout(title={
        'text': "Percentage of Sub-Regions Production of " + selected_region,
        'font': {'size': 18}
    })
    fig.update_traces(textposition='inside', textinfo='percent+label')

    return fig
############### Section Three

# 3.1 Commodities by region area graph




# 3.2 Commodities by region donut
@app.callback(
    Output("region_production_pie", "figure"),
    [Input("commodity_dropdown", "value")]
)
def update_region_production_pie(commodity):
    if commodity=='All':
        df_commodity=df
    else:
        df_commodity = df[df["Commodity"] == commodity]
    df_production_by_region = df_commodity.groupby("Region").sum()
    
    fig = px.pie(df_production_by_region, values="Production", names=df_production_by_region.index)
    fig.update_layout(title={
        'text': "Percentage of Regions Production of " + commodity + " commodity",
        'font': {'size': 18}
    })
    return fig


# 3.3 selected Commodities by sub-region for selected region









app.run_server(debug=True)







