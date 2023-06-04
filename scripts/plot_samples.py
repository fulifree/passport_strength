import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image

''' This script plots two sample images using the merged data '''

# Config plotly output if needed
'''
config = {
  'toImageButtonOptions': {
      'format': 'svg',
      'height': 500, 
      'width': 700, 
      'scale': 1
    }
}
'''

# Load data
df = pd.read_csv('../data/visa_population_income.csv', keep_default_na=False)

''' -------------------------------------------------- '''
''' Sample figure 1: visa exemption with country marks '''
''' -------------------------------------------------- '''
# Scatter visa exemption data
fig = go.Figure(data=[go.Scatter(
    x=df['total to'],
    y=df['total access'],
    text=df['Country Name'],
    mode='markers')])

# Manual list of flag images that aren't in github.com/matahombres/CSS-Country-Flags-Rounded
manual_flag = ['CI','SZ','MW','MY','NA','VA']

# Change scatter images to flags
for i, row in df.iterrows():
    country_iso = row["iso2"]
    if country_iso in manual_flag:
        flag = Image.open(f"../data/flags/{country_iso}.png")
    else:
        flag = f"https://raw.githubusercontent.com/matahombres/CSS-Country-Flags-Rounded/master/flags/{country_iso}.png"   
    fig.add_layout_image(
        dict(
            source=flag,
            xref="x",
            yref="y",
            xanchor="center",
            yanchor="middle",
            x=row["total to"],
            y=row["total access"],
            sizex=12,
            sizey=12,
            sizing="contain",
            opacity=0.8,
            layer="above"
        )
    )

# Edit figure title, axis titles, bg colors, etc.
fig.update_layout(
    title='Visa Exemption',
    xaxis=dict(
        title='Granting Number',
        gridcolor='white',
        gridwidth=2,
    ),
    yaxis=dict(
        title='Granted Number',
        gridcolor='white',
        gridwidth=2,
    ),
    paper_bgcolor='rgb(230, 230, 230)',
    plot_bgcolor='rgb(200, 200, 200)',
)

# Save the output figure
fig.write_image("../images/sample1_flags.png")

''' -------------------------------------------------------------- '''
''' Sample figure 2: visa exemption with population & income group '''
''' -------------------------------------------------------------- '''

# The 4 income groups in data
income_group = ['High income', 'Upper middle income', 'Lower middle income', 'Low income']

# Scatter the visa exemption data by income group
# Marker size reflects the population
fig = go.Figure()
for income in income_group:
    fig.add_trace(go.Scatter(
        x=df[df['IncomeGroup']==income]['total to'],
        y=df[df['IncomeGroup']==income]['total access'],
        text=df[df['IncomeGroup']==income]['Country Name'],
        name=income[:-7],
        marker_size=df[df['IncomeGroup']==income]['2021']
    ))

# Update the reference for mark size
sizeref = 1.*max(df['2021'])/(100**2)
fig.update_traces(mode='markers',
                  marker=dict(sizemode='area',
                              sizeref=sizeref, line_width=2))

# Update legend orientation and position
fig.update_layout(
    
)

# Edit figure title, axis titles, bg colors, etc.
fig.update_layout(
    title='Visa Exemption, population as marker size',
    xaxis=dict(
        title='Granting Number',
        gridcolor='white',
        gridwidth=2,
    ),
    yaxis=dict(
        title='Granted Number',
        gridcolor='white',
        gridwidth=2,
    ),
    legend_title_text='Income group',
    legend_traceorder='reversed',
    legend=dict(
        orientation='h',
        yanchor="top",
        y=1.1,
        xanchor="left",
        x=0.01
    ),
    paper_bgcolor='rgb(230, 230, 230)',
    plot_bgcolor='rgb(200, 200, 200)',
)

# Save the output figure
fig.write_image("../images/sample2_population_and_income_group.png")