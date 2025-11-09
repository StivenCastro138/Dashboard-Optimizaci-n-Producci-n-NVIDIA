import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# Inicializar la app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

# Datos
production_data = pd.DataFrame({
    'Producto': ['RTX 4090', 'RTX 4070', 'A100', 'H100'],
    'Cantidad': [2000, 5000, 0, 600],
    'Utilidad': [1698000, 1595000, 0, 9300000],
    'Unitaria': [849, 319, 5200, 15500],
    'Precio': [1599, 599, 10000, 30000],
    'Costo': [750, 280, 4800, 14500],
    'Color': ['#10b981', '#3b82f6', '#8b5cf6', '#f59e0b']
})

resource_data = pd.DataFrame({
    'Recurso': ['Horas Fabricación', 'Empaque', 'Memoria GDDR6X', 'Memoria HBM3', 'Presupuesto'],
    'Usado': [32000, 7600, 108000, 600, 20.2],
    'Disponible': [50000, 35000, 150000, 1000, 45],
    'Porcentaje': [64, 22, 72, 60, 45],
    'Unidad': ['hrs', 'unidades', 'GB', 'GB', 'M$']
})

shadow_prices = pd.DataFrame({
    'Recurso': ['Horas Fabricación', 'Empaque', 'GDDR6X', 'HBM3', 'Presupuesto'],
    'Precio': [0, 0, 0, 15500, 0],
    'Impacto': ['Nulo', 'Nulo', 'Nulo', 'Crítico', 'Nulo']
})

scenarios = pd.DataFrame({
    'Escenario': ['Base', '+20% HBM3', '+50% HBM3', '+20% Presup.'],
    'Utilidad': [12.59, 15.10, 19.39, 12.59],
    'HBM3': [1000, 1200, 1500, 1000],
    'Produccion': [7600, 8000, 8600, 7600]
})

simplex_data = pd.DataFrame({
    'Iteracion': [0, 1, 2, 3, 4],
    'Z': [0, 4.5, 8.75, 11.2, 12.59],
    'x1': [0, 0, 0, 1500, 2000],
    'x2': [0, 0, 2500, 4000, 5000],
    'x3': [0, 0, 0, 0, 0],
    'x4': [0, 290, 565, 580, 600]
})

sensitivity_data = pd.DataFrame({
    'Producto': ['RTX 4090', 'RTX 4070', 'A100', 'H100'],
    'Actual': [849, 319, 5200, 15500],
    'Minimo': [721, 271, 0, 14000],
    'Maximo': [977, 367, 16800, 17000],
    'Rango': ['±15%', '±15%', 'Amplio', '±10%'],
    'Estable': ['✓', '✓', '✗', '✓']
})

# Estilos
colors = {
    'background': '#f9fafb',
    'text': '#1f2937',
    'primary': '#10b981',
    'secondary': '#3b82f6',
    'warning': '#f59e0b',
    'danger': '#ef4444'
}

card_style = {
    'backgroundColor': 'white',
    'padding': '20px',
    'borderRadius': '10px',
    'boxShadow': '0 2px 8px rgba(0,0,0,0.1)',
    'marginBottom': '20px'
}

kpi_style = {
    'backgroundColor': 'white',
    'padding': '20px',
    'borderRadius': '10px',
    'boxShadow': '0 2px 8px rgba(0,0,0,0.1)',
    'borderLeft': '4px solid',
    'transition': 'transform 0.2s'
}

# Layout
app.layout = html.Div(style={'backgroundColor': colors['background'], 'padding': '20px'}, children=[
    # Header
    html.Div(style={'marginBottom': '30px'}, children=[
        html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'marginBottom': '20px'}, children=[
            html.Div([
                html.H1('🖥️ NVIDIA - Optimización de Producción', 
                       style={'color': colors['text'], 'marginBottom': '10px', 'fontSize': '36px', 'fontWeight': 'bold'}),
                html.P('Análisis mediante Programación Lineal y Método Simplex', 
                      style={'color': '#6b7280', 'fontSize': '16px'})
            ]),
            html.Div(style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '10px', 'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'}, children=[
                html.P('Método: Simplex', style={'margin': '0', 'fontSize': '14px', 'color': '#6b7280'}),
                html.P('Variables: 4 | Restricciones: 5', style={'margin': '0', 'fontSize': '14px', 'color': '#6b7280'}),
                html.P('Optimalidad alcanzada', style={'margin': '0', 'fontSize': '14px', 'color': colors['primary'], 'fontWeight': 'bold', 'marginTop': '5px'})
            ])
        ]),
        
        # Tabs
        html.Div(style={'backgroundColor': 'white', 'padding': '10px', 'borderRadius': '10px', 'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'}, children=[
            dcc.Tabs(id='tabs', value='overview', children=[
                dcc.Tab(label='📊 Resumen Ejecutivo', value='overview', 
                       style={'padding': '10px 20px', 'fontWeight': 'bold'},
                       selected_style={'padding': '10px 20px', 'fontWeight': 'bold', 'backgroundColor': colors['primary'], 'color': 'white'}),
                dcc.Tab(label='📦 Producción', value='production',
                       style={'padding': '10px 20px', 'fontWeight': 'bold'},
                       selected_style={'padding': '10px 20px', 'fontWeight': 'bold', 'backgroundColor': colors['primary'], 'color': 'white'}),
                dcc.Tab(label='⚡ Recursos', value='resources',
                       style={'padding': '10px 20px', 'fontWeight': 'bold'},
                       selected_style={'padding': '10px 20px', 'fontWeight': 'bold', 'backgroundColor': colors['primary'], 'color': 'white'}),
                dcc.Tab(label='📈 Sensibilidad', value='sensitivity',
                       style={'padding': '10px 20px', 'fontWeight': 'bold'},
                       selected_style={'padding': '10px 20px', 'fontWeight': 'bold', 'backgroundColor': colors['primary'], 'color': 'white'}),
                dcc.Tab(label='🔢 Simplex', value='simplex',
                       style={'padding': '10px 20px', 'fontWeight': 'bold'},
                       selected_style={'padding': '10px 20px', 'fontWeight': 'bold', 'backgroundColor': colors['primary'], 'color': 'white'}),
            ])
        ])
    ]),
    
    # Content
    html.Div(id='tab-content')
])

# Footer
def create_footer():
    return html.Footer(style={'marginTop': '60px', 'textAlign': 'center', 'color': '#9ca3af', 'fontSize': '14px', 'paddingBottom': '30px'}, children=[
        html.P('Dashboard de Optimización de Producción NVIDIA', style={'margin': '5px 0'}),
        html.P('Desarrollado con Dash + Plotly | Método Simplex aplicado', style={'margin': '5px 0'}),
        html.P('Yudid Paola Aguirre Martínez - Investigación de Operaciones', style={'margin': '5px 0'})
    ])

# Callback único para cambiar contenido
@app.callback(
    Output('tab-content', 'children'),
    Input('tabs', 'value')
)
def render_content(tab):
    if tab == 'overview':
        return html.Div([
            # KPIs
            html.Div(style={'display': 'grid', 'gridTemplateColumns': 'repeat(auto-fit, minmax(250px, 1fr))', 'gap': '20px', 'marginBottom': '30px'}, children=[
                html.Div(style={**kpi_style, 'borderLeftColor': colors['primary']}, children=[
                    html.P('💰 Utilidad Mensual Óptima', style={'color': '#6b7280', 'fontSize': '14px', 'margin': '0'}),
                    html.H2('$12.59M', style={'color': colors['primary'], 'fontSize': '32px', 'margin': '10px 0'}),
                    html.P('Máxima utilidad alcanzable', style={'color': '#9ca3af', 'fontSize': '12px', 'margin': '0'}),
                    html.P('📈 +100% optimizado', style={'color': colors['primary'], 'fontSize': '14px', 'fontWeight': 'bold', 'marginTop': '10px'})
                ]),
                html.Div(style={**kpi_style, 'borderLeftColor': colors['secondary']}, children=[
                    html.P('📦 Unidades Totales', style={'color': '#6b7280', 'fontSize': '14px', 'margin': '0'}),
                    html.H2('7,600', style={'color': colors['secondary'], 'fontSize': '32px', 'margin': '10px 0'}),
                    html.P('Mix óptimo de producción', style={'color': '#9ca3af', 'fontSize': '12px', 'margin': '0'}),
                ]),
                html.Div(style={**kpi_style, 'borderLeftColor': colors['warning']}, children=[
                    html.P('🌟 Producto Estrella', style={'color': '#6b7280', 'fontSize': '14px', 'margin': '0'}),
                    html.H2('H100', style={'color': colors['warning'], 'fontSize': '32px', 'margin': '10px 0'}),
                    html.P('74% de la utilidad total', style={'color': '#9ca3af', 'fontSize': '12px', 'margin': '0'}),
                    html.P('📈 $15.5K/unidad', style={'color': colors['warning'], 'fontSize': '14px', 'fontWeight': 'bold', 'marginTop': '10px'})
                ]),
                html.Div(style={**kpi_style, 'borderLeftColor': colors['danger']}, children=[
                    html.P('⚠️ Cuello de Botella', style={'color': '#6b7280', 'fontSize': '14px', 'margin': '0'}),
                    html.H2('HBM3', style={'color': colors['danger'], 'fontSize': '32px', 'margin': '10px 0'}),
                    html.P('Precio sombra: $15.5K/GB', style={'color': '#9ca3af', 'fontSize': '12px', 'margin': '0'}),
                ]),
            ]),
            
            # Gráficos principales
            html.Div(style={'display': 'grid', 'gridTemplateColumns': 'repeat(auto-fit, minmax(500px, 1fr))', 'gap': '20px', 'marginBottom': '30px'}, children=[
                html.Div(style=card_style, children=[
                    html.H3('💰 Contribución a la Utilidad', style={'marginBottom': '20px', 'color': colors['text']}),
                    dcc.Graph(
                        figure=px.pie(
                            production_data,
                            values='Utilidad',
                            names='Producto',
                            color='Producto',
                            color_discrete_map={'RTX 4090': '#10b981', 'RTX 4070': '#3b82f6', 'A100': '#8b5cf6', 'H100': '#f59e0b'},
                            hole=0.4
                        ).update_layout(
                            showlegend=True,
                            height=400,
                            margin=dict(t=20, b=20, l=20, r=20)
                        )
                    ),
                    html.P('H100 genera 3 de cada 4 dólares de utilidad', 
                          style={'textAlign': 'center', 'color': '#6b7280', 'fontSize': '14px', 'marginTop': '10px'})
                ]),
                html.Div(style=card_style, children=[
                    html.H3('📦 Mix de Producción Óptimo', style={'marginBottom': '20px', 'color': colors['text']}),
                    dcc.Graph(
                        figure=go.Figure(data=[
                            go.Bar(
                                x=production_data['Producto'],
                                y=production_data['Cantidad'],
                                marker_color=production_data['Color'],
                                text=production_data['Cantidad'],
                                textposition='auto',
                            )
                        ]).update_layout(
                            xaxis_title='Producto',
                            yaxis_title='Cantidad',
                            showlegend=False,
                            height=400,
                            margin=dict(t=20, b=40, l=40, r=20)
                        )
                    )
                ])
            ]),
            
            # Hallazgos clave
            html.Div(style={'background': 'linear-gradient(to right, #d1fae5, #dbeafe)', 'padding': '30px', 'borderRadius': '10px', 'borderLeft': '4px solid ' + colors['primary']}, children=[
                html.H3('✅ Hallazgos Clave', style={'marginBottom': '20px', 'color': colors['text']}),
                html.Div(style={'display': 'grid', 'gridTemplateColumns': 'repeat(auto-fit, minmax(250px, 1fr))', 'gap': '15px'}, children=[
                    html.Div(style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}, children=[
                        html.H4('✓ Enfoque en H100', style={'color': colors['primary'], 'marginBottom': '10px'}),
                        html.P('Solo 8% del volumen pero 74% de las utilidades. Máxima eficiencia de capital.',
                              style={'color': colors['text'], 'fontSize': '14px', 'margin': '0'})
                    ]),
                    html.Div(style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}, children=[
                        html.H4('⚠ Subutilización', style={'color': colors['warning'], 'marginBottom': '10px'}),
                        html.P('78% del empaque sin usar, 55% del presupuesto disponible. Oportunidad de expansión.',
                              style={'color': colors['text'], 'fontSize': '14px', 'margin': '0'})
                    ]),
                    html.Div(style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}, children=[
                        html.H4('🎯 Cuello de Botella', style={'color': colors['danger'], 'marginBottom': '10px'}),
                        html.P('Memoria HBM3 es el único limitante real. Cada GB adicional = +$15.5K utilidad.',
                              style={'color': colors['text'], 'fontSize': '14px', 'margin': '0'})
                    ])
                ])
            ])
        ])
    
    elif tab == 'production':
        return html.Div([
            html.Div(style={'display': 'grid', 'gridTemplateColumns': 'repeat(auto-fit, minmax(500px, 1fr))', 'gap': '20px', 'marginBottom': '30px'}, children=[
                html.Div(style=card_style, children=[
                    html.H3('📊 Utilidad por Producto', style={'marginBottom': '20px'}),
                    dcc.Graph(
                        figure=go.Figure(data=[
                            go.Bar(
                                y=production_data['Producto'],
                                x=production_data['Utilidad'],
                                orientation='h',
                                marker_color=production_data['Color'],
                                text=[f"${x/1000000:.2f}M" for x in production_data['Utilidad']],
                                textposition='auto',
                            )
                        ]).update_layout(
                            xaxis_title='Utilidad ($)',
                            yaxis_title='',
                            showlegend=False,
                            height=400
                        )
                    )
                ]),
                html.Div(style=card_style, children=[
                    html.H3('💵 Precio vs Costo vs Utilidad', style={'marginBottom': '20px'}),
                    dcc.Graph(
                        figure=go.Figure(data=[
                            go.Bar(name='Precio', x=production_data['Producto'], y=production_data['Precio'], marker_color='#3b82f6'),
                            go.Bar(name='Costo', x=production_data['Producto'], y=production_data['Costo'], marker_color='#ef4444'),
                            go.Bar(name='Utilidad', x=production_data['Producto'], y=production_data['Unitaria'], marker_color='#10b981')
                        ]).update_layout(
                            barmode='group',
                            height=400,
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                        )
                    )
                ])
            ]),
            
            # Tabla detallada
            html.Div(style=card_style, children=[
                html.H3('📋 Detalle de Producción Óptima', style={'marginBottom': '20px'}),
                html.Table(style={'width': '100%', 'borderCollapse': 'collapse'}, children=[
                    html.Thead(children=[
                        html.Tr(style={'backgroundColor': '#f3f4f6'}, children=[
                            html.Th('Producto', style={'padding': '12px', 'textAlign': 'left', 'borderBottom': '2px solid #e5e7eb'}),
                            html.Th('Cantidad', style={'padding': '12px', 'textAlign': 'right', 'borderBottom': '2px solid #e5e7eb'}),
                            html.Th('Precio', style={'padding': '12px', 'textAlign': 'right', 'borderBottom': '2px solid #e5e7eb'}),
                            html.Th('Costo', style={'padding': '12px', 'textAlign': 'right', 'borderBottom': '2px solid #e5e7eb'}),
                            html.Th('Util. Unit.', style={'padding': '12px', 'textAlign': 'right', 'borderBottom': '2px solid #e5e7eb'}),
                            html.Th('Utilidad Total', style={'padding': '12px', 'textAlign': 'right', 'borderBottom': '2px solid #e5e7eb'}),
                            html.Th('% Contrib.', style={'padding': '12px', 'textAlign': 'right', 'borderBottom': '2px solid #e5e7eb'}),
                            html.Th('Status', style={'padding': '12px', 'textAlign': 'center', 'borderBottom': '2px solid #e5e7eb'}),
                        ])
                    ]),
                    html.Tbody(children=[
                        html.Tr(style={'borderBottom': '1px solid #e5e7eb'}, children=[
                            html.Td(row['Producto'], style={'padding': '12px', 'fontWeight': 'bold'}),
                            html.Td(f"{row['Cantidad']:,}", style={'padding': '12px', 'textAlign': 'right'}),
                            html.Td(f"${row['Precio']:,}", style={'padding': '12px', 'textAlign': 'right'}),
                            html.Td(f"${row['Costo']:,}", style={'padding': '12px', 'textAlign': 'right'}),
                            html.Td(f"${row['Unitaria']:,}", style={'padding': '12px', 'textAlign': 'right'}),
                            html.Td(f"${row['Utilidad']/1000000:.2f}M", style={'padding': '12px', 'textAlign': 'right', 'fontWeight': 'bold'}),
                            html.Td(f"{(row['Utilidad']/12593000*100):.1f}%", style={'padding': '12px', 'textAlign': 'right'}),
                            html.Td(
                                html.Span('Producir' if row['Cantidad'] > 0 else 'No producir',
                                         style={
                                             'padding': '5px 10px',
                                             'borderRadius': '20px',
                                             'fontSize': '12px',
                                             'fontWeight': 'bold',
                                             'backgroundColor': '#d1fae5' if row['Cantidad'] > 0 else '#fee2e2',
                                             'color': '#065f46' if row['Cantidad'] > 0 else '#991b1b'
                                         }),
                                style={'padding': '12px', 'textAlign': 'center'}
                            ),
                        ]) for idx, row in production_data.iterrows()
                    ] + [
                        html.Tr(style={'backgroundColor': '#f3f4f6', 'fontWeight': 'bold'}, children=[
                            html.Td('TOTAL', style={'padding': '12px'}),
                            html.Td('7,600', style={'padding': '12px', 'textAlign': 'right'}),
                            html.Td('—', style={'padding': '12px', 'textAlign': 'right'}),
                            html.Td('—', style={'padding': '12px', 'textAlign': 'right'}),
                            html.Td('—', style={'padding': '12px', 'textAlign': 'right'}),
                            html.Td('$12.59M', style={'padding': '12px', 'textAlign': 'right'}),
                            html.Td('100%', style={'padding': '12px', 'textAlign': 'right'}),
                            html.Td('', style={'padding': '12px'}),
                        ])
                    ])
                ])
            ]),
            
            # Cards de productos
            html.Div(style={'display': 'grid', 'gridTemplateColumns': 'repeat(auto-fit, minmax(200px, 1fr))', 'gap': '15px', 'marginTop': '20px'}, children=[
                html.Div(style={**card_style, 'borderTop': f'4px solid {row["Color"]}'}, children=[
                    html.H4(row['Producto'], style={'marginBottom': '10px', 'color': colors['text']}),
                    html.H2(f"{row['Cantidad']:,}", style={'margin': '5px 0', 'color': row['Color'], 'fontSize': '28px'}),
                    html.P('unidades/mes', style={'fontSize': '12px', 'color': '#9ca3af', 'margin': '0'}),
                    html.Hr(style={'margin': '15px 0', 'border': 'none', 'borderTop': '1px solid #e5e7eb'}),
                    html.P(f"Utilidad: ${row['Utilidad']/1000000:.2f}M", style={'fontSize': '14px', 'margin': '5px 0'}),
                    html.P(f"Margen: {(row['Unitaria']/row['Precio']*100):.1f}%", style={'fontSize': '12px', 'color': '#6b7280', 'margin': '5px 0'})
                ]) for idx, row in production_data.iterrows()
            ])
        ])
    
    elif tab == 'resources':
        return html.Div([
            html.Div(style=card_style, children=[
                html.H3('⚡ Utilización de Recursos', style={'marginBottom': '20px'}),
                dcc.Graph(
                    figure=go.Figure(data=[
                        go.Bar(
                            y=resource_data['Recurso'],
                            x=resource_data['Porcentaje'],
                            orientation='h',
                            marker=dict(
                                color=resource_data['Porcentaje'],
                                colorscale=[[0, '#10b981'], [0.5, '#f59e0b'], [1, '#ef4444']],
                                cmin=0,
                                cmax=100
                            ),
                            text=[f"{x}%" for x in resource_data['Porcentaje']],
                            textposition='auto',
                        )
                    ]).update_layout(
                        xaxis_title='% Utilizado',
                        xaxis=dict(range=[0, 100]),
                        yaxis_title='',
                        showlegend=False,
                        height=400
                    )
                )
            ]),
            
            html.Div(style={'display': 'grid', 'gridTemplateColumns': 'repeat(auto-fit, minmax(500px, 1fr))', 'gap': '20px', 'marginTop': '20px'}, children=[
                html.Div(style=card_style, children=[
                    html.H3('🔍 Precios Sombra', style={'marginBottom': '10px'}),
                    html.P('Valor marginal de cada unidad adicional de recurso', style={'fontSize': '14px', 'color': '#6b7280', 'marginBottom': '20px'}),
                    html.Div(children=[
                        html.Div(style={
                            'padding': '15px',
                            'marginBottom': '10px',
                            'backgroundColor': '#f9fafb',
                            'borderRadius': '8px',
                            'borderLeft': f'4px solid {"#ef4444" if row["Precio"] > 0 else "#9ca3af"}'
                        }, children=[
                            html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'}, children=[
                                html.Div([
                                    html.P(row['Recurso'], style={'fontWeight': 'bold', 'margin': '0', 'fontSize': '16px'}),
                                    html.P(f"Impacto: {row['Impacto']}", style={'fontSize': '14px', 'color': '#6b7280', 'margin': '5px 0 0 0'})
                                ]),
                                html.Div(style={'textAlign': 'right'}, children=[
                                    html.H3(f"${row['Precio']:,}", style={
                                        'margin': '0',
                                        'color': '#ef4444' if row['Precio'] > 0 else '#9ca3af',
                                        'fontSize': '24px'
                                    }),
                                    html.P('por unidad', style={'fontSize': '12px', 'color': '#9ca3af', 'margin': '5px 0 0 0'})
                                ])
                            ])
                        ]) for idx, row in shadow_prices.iterrows()
                    ])
                ]),
                
                html.Div(style=card_style, children=[
                    html.H3('📊 Perfil de Utilización', style={'marginBottom': '20px'}),
                    dcc.Graph(
                        figure=go.Figure(data=go.Scatterpolar(
                            r=resource_data['Porcentaje'],
                            theta=resource_data['Recurso'],
                            fill='toself',
                            fillcolor='rgba(59, 130, 246, 0.5)',
                            line=dict(color='#3b82f6', width=2)
                        )).update_layout(
                            polar=dict(
                                radialaxis=dict(visible=True, range=[0, 100])
                            ),
                            showlegend=False,
                            height=400
                        )
                    )
                ])
            ]),
            
            # Tabla de recursos
            html.Div(style=card_style, children=[
                html.H3('📋 Detalle de Recursos', style={'marginBottom': '20px'}),
                html.Table(style={'width': '100%', 'borderCollapse': 'collapse'}, children=[
                    html.Thead(children=[
                        html.Tr(style={'backgroundColor': '#f3f4f6'}, children=[
                            html.Th('Recurso', style={'padding': '12px', 'textAlign': 'left', 'borderBottom': '2px solid #e5e7eb'}),
                            html.Th('Usado', style={'padding': '12px', 'textAlign': 'right', 'borderBottom': '2px solid #e5e7eb'}),
                            html.Th('Disponible', style={'padding': '12px', 'textAlign': 'right', 'borderBottom': '2px solid #e5e7eb'}),
                            html.Th('Holgura', style={'padding': '12px', 'textAlign': 'right', 'borderBottom': '2px solid #e5e7eb'}),
                            html.Th('% Uso', style={'padding': '12px', 'textAlign': 'right', 'borderBottom': '2px solid #e5e7eb'}),
                            html.Th('Estado', style={'padding': '12px', 'textAlign': 'center', 'borderBottom': '2px solid #e5e7eb'}),
                            html.Th('Precio Sombra', style={'padding': '12px', 'textAlign': 'right', 'borderBottom': '2px solid #e5e7eb'}),
                        ])
                    ]),
                    html.Tbody(children=[
                        html.Tr(style={'borderBottom': '1px solid #e5e7eb'}, children=[
                            html.Td(row['Recurso'], style={'padding': '12px', 'fontWeight': 'bold'}),
                            html.Td(f"{row['Usado']:,} {row['Unidad']}", style={'padding': '12px', 'textAlign': 'right'}),
                            html.Td(f"{row['Disponible']:,} {row['Unidad']}", style={'padding': '12px', 'textAlign': 'right'}),
                            html.Td(f"{(row['Disponible']-row['Usado']):,} {row['Unidad']}", style={'padding': '12px', 'textAlign': 'right'}),
                            html.Td(f"{row['Porcentaje']}%", style={'padding': '12px', 'textAlign': 'right', 'fontWeight': 'bold'}),
                            html.Td(
                                html.Span(
                                    'Crítico' if row['Porcentaje'] > 80 else 'Moderado' if row['Porcentaje'] > 50 else 'Disponible',
                                    style={
                                        'padding': '5px 10px',
                                        'borderRadius': '20px',
                                        'fontSize': '12px',
                                        'fontWeight': 'bold',
                                        'backgroundColor': '#fee2e2' if row['Porcentaje'] > 80 else '#fef3c7' if row['Porcentaje'] > 50 else '#d1fae5',
                                        'color': '#991b1b' if row['Porcentaje'] > 80 else '#92400e' if row['Porcentaje'] > 50 else '#065f46'
                                    }
                                ),
                                style={'padding': '12px', 'textAlign': 'center'}
                            ),
                            html.Td(f"${shadow_prices.iloc[idx]['Precio']:,}", style={'padding': '12px', 'textAlign': 'right', 'fontWeight': 'bold'}),
                        ]) for idx, row in resource_data.iterrows()
                    ])
                ])
            ])
        ])
    
    elif tab == 'sensitivity':
        return html.Div([
            html.Div(style=card_style, children=[
                html.H3('📈 Análisis de Escenarios', style={'marginBottom': '20px'}),
                html.Div(style={'display': 'flex', 'gap': '10px', 'marginBottom': '20px', 'flexWrap': 'wrap'}, children=[
                    html.Button(
                        row['Escenario'],
                        id={'type': 'scenario-btn', 'index': idx},
                        n_clicks=0,
                        style={
                            'padding': '12px 24px',
                            'borderRadius': '8px',
                            'border': 'none',
                            'fontWeight': 'bold',
                            'cursor': 'pointer',
                            'backgroundColor': colors['primary'] if idx == 0 else '#f3f4f6',
                            'color': 'white' if idx == 0 else '#6b7280',
                            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)' if idx == 0 else 'none'
                        }
                    ) for idx, row in scenarios.iterrows()
                ]),
                
                html.Div(style={'display': 'grid', 'gridTemplateColumns': 'repeat(auto-fit, minmax(250px, 1fr))', 'gap': '15px'}, children=[
                    html.Div(style={'background': 'linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%)', 'padding': '20px', 'borderRadius': '10px'}, children=[
                        html.P('💰 Utilidad Proyectada', style={'color': '#6b7280', 'fontSize': '14px', 'margin': '0 0 10px 0'}),
                        html.H2(f"${scenarios.iloc[0]['Utilidad']}M", style={'color': colors['primary'], 'fontSize': '32px', 'margin': '0'}),
                    ]),
                    html.Div(style={'background': 'linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%)', 'padding': '20px', 'borderRadius': '10px'}, children=[
                        html.P('🧠 Memoria HBM3', style={'color': '#6b7280', 'fontSize': '14px', 'margin': '0 0 10px 0'}),
                        html.H2(f"{scenarios.iloc[0]['HBM3']} GB", style={'color': colors['secondary'], 'fontSize': '32px', 'margin': '0'}),
                    ]),
                    html.Div(style={'background': 'linear-gradient(135deg, #e9d5ff 0%, #d8b4fe 100%)', 'padding': '20px', 'borderRadius': '10px'}, children=[
                        html.P('📦 Producción Total', style={'color': '#6b7280', 'fontSize': '14px', 'margin': '0 0 10px 0'}),
                        html.H2(f"{scenarios.iloc[0]['Produccion']:,}", style={'color': '#8b5cf6', 'fontSize': '32px', 'margin': '0'}),
                    ]),
                ])
            ]),
            
            html.Div(style=card_style, children=[
                html.H3('📊 Comparación de Escenarios', style={'marginBottom': '20px'}),
                dcc.Graph(
                    figure=px.line(
                        scenarios,
                        x='Escenario',
                        y='Utilidad',
                        markers=True,
                        title='Utilidad por Escenario'
                    ).update_traces(
                        line=dict(color=colors['primary'], width=3),
                        marker=dict(size=10)
                    ).update_layout(
                        xaxis_title='',
                        yaxis_title='Utilidad (M$)',
                        height=400
                    )
                )
            ]),
            
            html.Div(style=card_style, children=[
                html.H3('📋 Rangos de Estabilidad - Utilidades Unitarias', style={'marginBottom': '20px'}),
                html.Table(style={'width': '100%', 'borderCollapse': 'collapse'}, children=[
                    html.Thead(children=[
                        html.Tr(style={'backgroundColor': '#f3f4f6'}, children=[
                            html.Th('Producto', style={'padding': '12px', 'textAlign': 'left', 'borderBottom': '2px solid #e5e7eb'}),
                            html.Th('Utilidad Actual', style={'padding': '12px', 'textAlign': 'right', 'borderBottom': '2px solid #e5e7eb'}),
                            html.Th('Mínimo', style={'padding': '12px', 'textAlign': 'right', 'borderBottom': '2px solid #e5e7eb'}),
                            html.Th('Máximo', style={'padding': '12px', 'textAlign': 'right', 'borderBottom': '2px solid #e5e7eb'}),
                            html.Th('Rango', style={'padding': '12px', 'textAlign': 'center', 'borderBottom': '2px solid #e5e7eb'}),
                            html.Th('Estabilidad', style={'padding': '12px', 'textAlign': 'center', 'borderBottom': '2px solid #e5e7eb'}),
                        ])
                    ]),
                    html.Tbody(children=[
                        html.Tr(style={'borderBottom': '1px solid #e5e7eb'}, children=[
                            html.Td(row['Producto'], style={'padding': '12px', 'fontWeight': 'bold'}),
                            html.Td(f"${row['Actual']:,}", style={'padding': '12px', 'textAlign': 'right', 'fontWeight': 'bold'}),
                            html.Td(f"${row['Minimo']:,}", style={'padding': '12px', 'textAlign': 'right'}),
                            html.Td(f"${row['Maximo']:,}", style={'padding': '12px', 'textAlign': 'right'}),
                            html.Td(row['Rango'], style={'padding': '12px', 'textAlign': 'center'}),
                            html.Td(
                                html.Span(
                                    'Estable' if row['Estable'] == '✓' else 'Inestable',
                                    style={
                                        'padding': '5px 10px',
                                        'borderRadius': '20px',
                                        'fontSize': '12px',
                                        'fontWeight': 'bold',
                                        'backgroundColor': '#d1fae5' if row['Estable'] == '✓' else '#fef3c7',
                                        'color': '#065f46' if row['Estable'] == '✓' else '#92400e'
                                    }
                                ),
                                style={'padding': '12px', 'textAlign': 'center'}
                            ),
                        ]) for idx, row in sensitivity_data.iterrows()
                    ])
                ]),
                html.Div(style={'marginTop': '20px', 'padding': '15px', 'backgroundColor': '#dbeafe', 'borderRadius': '8px'}, children=[
                    html.P([
                        html.Strong('Nota: '),
                        'El A100 necesitaría una utilidad unitaria de ',
                        html.Strong('$16,800'),
                        ' (vs actual $5,200) para entrar en el plan óptimo. Un incremento de ',
                        html.Strong('+223%'),
                        '.'
                    ], style={'margin': '0', 'fontSize': '14px', 'color': colors['text']})
                ])
            ]),
            
            html.Div(style=card_style, children=[
                html.H3('📊 Visualización de Rangos de Sensibilidad', style={'marginBottom': '20px'}),
                dcc.Graph(
                    figure=go.Figure(data=[
                        go.Bar(name='Mínimo', x=sensitivity_data['Producto'], y=sensitivity_data['Minimo'], marker_color='#ef4444'),
                        go.Bar(name='Actual', x=sensitivity_data['Producto'], y=sensitivity_data['Actual'], marker_color='#3b82f6'),
                        go.Bar(name='Máximo', x=sensitivity_data['Producto'], y=sensitivity_data['Maximo'], marker_color='#10b981')
                    ]).update_layout(
                        barmode='group',
                        xaxis_title='',
                        yaxis_title='Utilidad Unitaria ($)',
                        height=400,
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )
                )
            ])
        ])
    
    elif tab == 'simplex':
        return html.Div([
            html.Div(style=card_style, children=[
                html.H3('🔢 Convergencia del Método Simplex', style={'marginBottom': '20px'}),
                dcc.Graph(
                    figure=px.line(
                        simplex_data,
                        x='Iteracion',
                        y='Z',
                        markers=True,
                        title='Evolución de la Función Objetivo'
                    ).update_traces(
                        line=dict(color=colors['primary'], width=3),
                        marker=dict(size=10)
                    ).update_layout(
                        xaxis_title='Iteración',
                        yaxis_title='Utilidad (M$)',
                        height=400
                    )
                ),
                html.Div(style={'marginTop': '15px', 'padding': '15px', 'backgroundColor': '#d1fae5', 'borderRadius': '8px'}, children=[
                    html.P([
                        'El algoritmo Simplex convergió en ',
                        html.Strong('4 iteraciones'),
                        ', alcanzando la solución óptima de ',
                        html.Strong('$12.59M'),
                        ' de utilidad mensual.'
                    ], style={'margin': '0', 'fontSize': '14px', 'color': colors['text']})
                ])
            ]),
            
            html.Div(style=card_style, children=[
                html.H3('📈 Evolución de Variables por Iteración', style={'marginBottom': '20px'}),
                dcc.Graph(
                    figure=go.Figure(data=[
                        go.Scatter(x=simplex_data['Iteracion'], y=simplex_data['x1'], mode='lines+markers', name='RTX 4090 (x₁)', line=dict(color='#10b981', width=2)),
                        go.Scatter(x=simplex_data['Iteracion'], y=simplex_data['x2'], mode='lines+markers', name='RTX 4070 (x₂)', line=dict(color='#3b82f6', width=2)),
                        go.Scatter(x=simplex_data['Iteracion'], y=simplex_data['x3'], mode='lines+markers', name='A100 (x₃)', line=dict(color='#8b5cf6', width=2)),
                        go.Scatter(x=simplex_data['Iteracion'], y=simplex_data['x4'], mode='lines+markers', name='H100 (x₄)', line=dict(color='#f59e0b', width=2))
                    ]).update_layout(
                        xaxis_title='Iteración',
                        yaxis_title='Cantidad',
                        height=400,
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )
                )
            ]),
            
            html.Div(style=card_style, children=[
                html.H3('📋 Tabla de Iteraciones del Simplex', style={'marginBottom': '20px'}),
                html.Table(style={'width': '100%', 'borderCollapse': 'collapse'}, children=[
                    html.Thead(children=[
                        html.Tr(style={'backgroundColor': '#f3f4f6'}, children=[
                            html.Th('Iteración', style={'padding': '12px', 'textAlign': 'center', 'borderBottom': '2px solid #e5e7eb'}),
                            html.Th('Z (M$)', style={'padding': '12px', 'textAlign': 'right', 'borderBottom': '2px solid #e5e7eb'}),
                            html.Th('x₁ (4090)', style={'padding': '12px', 'textAlign': 'right', 'borderBottom': '2px solid #e5e7eb'}),
                            html.Th('x₂ (4070)', style={'padding': '12px', 'textAlign': 'right', 'borderBottom': '2px solid #e5e7eb'}),
                            html.Th('x₃ (A100)', style={'padding': '12px', 'textAlign': 'right', 'borderBottom': '2px solid #e5e7eb'}),
                            html.Th('x₄ (H100)', style={'padding': '12px', 'textAlign': 'right', 'borderBottom': '2px solid #e5e7eb'}),
                            html.Th('Estado', style={'padding': '12px', 'textAlign': 'center', 'borderBottom': '2px solid #e5e7eb'}),
                        ])
                    ]),
                    html.Tbody(children=[
                        html.Tr(style={'borderBottom': '1px solid #e5e7eb', 'backgroundColor': '#d1fae5' if idx == len(simplex_data) - 1 else 'white', 'fontWeight': 'bold' if idx == len(simplex_data) - 1 else 'normal'}, children=[
                            html.Td(str(row['Iteracion']), style={'padding': '12px', 'textAlign': 'center'}),
                            html.Td(f"${row['Z']:.2f}M", style={'padding': '12px', 'textAlign': 'right'}),
                            html.Td(f"{row['x1']:,}", style={'padding': '12px', 'textAlign': 'right'}),
                            html.Td(f"{row['x2']:,}", style={'padding': '12px', 'textAlign': 'right'}),
                            html.Td(f"{row['x3']:,}", style={'padding': '12px', 'textAlign': 'right'}),
                            html.Td(f"{row['x4']:,}", style={'padding': '12px', 'textAlign': 'right'}),
                            html.Td(
                                html.Span(
                                    'ÓPTIMO' if idx == len(simplex_data) - 1 else 'Iterando',
                                    style={
                                        'padding': '5px 10px',
                                        'borderRadius': '20px',
                                        'fontSize': '12px',
                                        'fontWeight': 'bold',
                                        'backgroundColor': colors['primary'] if idx == len(simplex_data) - 1 else '#dbeafe',
                                        'color': 'white' if idx == len(simplex_data) - 1 else '#1e40af'
                                    }
                                ),
                                style={'padding': '12px', 'textAlign': 'center'}
                            ),
                        ]) for idx, row in simplex_data.iterrows()
                    ])
                ])
            ]),
            
            html.Div(style={'display': 'grid', 'gridTemplateColumns': 'repeat(auto-fit, minmax(400px, 1fr))', 'gap': '20px', 'marginTop': '20px'}, children=[
                html.Div(style={'background': 'linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%)', 'padding': '25px', 'borderRadius': '10px', 'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'}, children=[
                    html.H4('📐 Modelo Matemático', style={'marginBottom': '15px', 'color': colors['text']}),
                    html.Div(style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '8px'}, children=[
                        html.P('Función Objetivo:', style={'fontWeight': 'bold', 'color': colors['secondary'], 'marginBottom': '10px'}),
                        html.P('max Z = 849x₁ + 319x₂ + 5200x₃ + 15500x₄', style={'fontFamily': 'monospace', 'fontSize': '12px', 'marginBottom': '15px'}),
                        
                        html.P('Restricciones:', style={'fontWeight': 'bold', 'color': colors['secondary'], 'marginBottom': '10px'}),
                        html.Div(style={'fontFamily': 'monospace', 'fontSize': '11px'}, children=[
                            html.P('8x₁ + 5x₂ + 12x₃ + 15x₄ ≤ 50,000', style={'margin': '5px 0'}),
                            html.P('x₁ + x₂ + x₃ + x₄ ≤ 35,000', style={'margin': '5px 0'}),
                            html.P('24x₁ + 12x₂ ≤ 150,000', style={'margin': '5px 0'}),
                            html.P('x₃ + x₄ ≤ 1,000', style={'margin': '5px 0'}),
                            html.P('750x₁ + 280x₂ + 4800x₃ + 14500x₄ ≤ 45,000,000', style={'margin': '5px 0'}),
                            html.P('x₁, x₂, x₃, x₄ ≥ 0', style={'margin': '5px 0'})
                        ])
                    ])
                ]),
                
                html.Div(style={'background': 'linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%)', 'padding': '25px', 'borderRadius': '10px', 'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'}, children=[
                    html.H4('✅ Solución Óptima', style={'marginBottom': '15px', 'color': colors['text']}),
                    html.Div(style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '8px'}, children=[
                        html.P('Variables de Decisión:', style={'fontSize': '14px', 'color': '#6b7280', 'marginBottom': '15px'}),
                        html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '10px', 'marginBottom': '15px'}, children=[
                            html.Div(style={'backgroundColor': '#d1fae5', 'padding': '10px', 'borderRadius': '8px'}, children=[
                                html.P('x₁ (RTX 4090)', style={'fontSize': '12px', 'color': '#6b7280', 'margin': '0'}),
                                html.P('2,000', style={'fontSize': '18px', 'fontWeight': 'bold', 'color': colors['primary'], 'margin': '5px 0 0 0'})
                            ]),
                            html.Div(style={'backgroundColor': '#dbeafe', 'padding': '10px', 'borderRadius': '8px'}, children=[
                                html.P('x₂ (RTX 4070)', style={'fontSize': '12px', 'color': '#6b7280', 'margin': '0'}),
                                html.P('5,000', style={'fontSize': '18px', 'fontWeight': 'bold', 'color': colors['secondary'], 'margin': '5px 0 0 0'})
                            ]),
                            html.Div(style={'backgroundColor': '#e9d5ff', 'padding': '10px', 'borderRadius': '8px'}, children=[
                                html.P('x₃ (A100)', style={'fontSize': '12px', 'color': '#6b7280', 'margin': '0'}),
                                html.P('0', style={'fontSize': '18px', 'fontWeight': 'bold', 'color': '#8b5cf6', 'margin': '5px 0 0 0'})
                            ]),
                            html.Div(style={'backgroundColor': '#fed7aa', 'padding': '10px', 'borderRadius': '8px'}, children=[
                                html.P('x₄ (H100)', style={'fontSize': '12px', 'color': '#6b7280', 'margin': '0'}),
                                html.P('600', style={'fontSize': '18px', 'fontWeight': 'bold', 'color': colors['warning'], 'margin': '5px 0 0 0'})
                            ])
                        ]),
                        html.Div(style={'paddingTop': '15px', 'borderTop': '1px solid #e5e7eb'}, children=[
                            html.P('Utilidad Máxima:', style={'fontSize': '14px', 'color': '#6b7280', 'margin': '0'}),
                            html.H2('$12.59M', style={'color': colors['primary'], 'fontSize': '32px', 'margin': '10px 0 0 0'})
                        ])
                    ])
                ])
            ]),
            
            html.Div(style={'background': 'linear-gradient(to right, #fae8ff, #f3e8ff)', 'padding': '30px', 'borderRadius': '10px', 'borderLeft': '4px solid #8b5cf6', 'marginTop': '20px'}, children=[
                html.H3('🔍 Interpretación del Simplex', style={'marginBottom': '20px', 'color': colors['text']}),
                html.Div(style={'display': 'grid', 'gridTemplateColumns': 'repeat(auto-fit, minmax(250px, 1fr))', 'gap': '15px'}, children=[
                    html.Div(style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}, children=[
                        html.H4('🔄 Proceso Iterativo', style={'color': '#8b5cf6', 'marginBottom': '10px', 'fontSize': '16px'}),
                        html.P('El algoritmo comenzó en el origen (iteración 0) y exploró vértices de la región factible, mejorando la función objetivo en cada paso hasta alcanzar el óptimo.',
                              style={'color': colors['text'], 'fontSize': '14px', 'margin': '0', 'lineHeight': '1.6'})
                    ]),
                    html.Div(style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}, children=[
                        html.H4('✅ Variables Básicas', style={'color': '#8b5cf6', 'marginBottom': '10px', 'fontSize': '16px'}),
                        html.P('En la solución óptima, las variables básicas son x₁, x₂ y x₄. La variable x₃ (A100) permanece en cero, indicando que no es rentable producirla.',
                              style={'color': colors['text'], 'fontSize': '14px', 'margin': '0', 'lineHeight': '1.6'})
                    ]),
                    html.Div(style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}, children=[
                        html.H4('📈 Mejora Progresiva', style={'color': '#8b5cf6', 'marginBottom': '10px', 'fontSize': '16px'}),
                        html.P('Cada iteración incrementó Z significativamente: de $0 a $4.5M (+∞%), luego a $8.75M (+94%), a $11.2M (+28%), y finalmente a $12.59M (+12%).',
                              style={'color': colors['text'], 'fontSize': '14px', 'margin': '0', 'lineHeight': '1.6'})
                    ]),
                    html.Div(style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}, children=[
                        html.H4('🎯 Optimalidad', style={'color': '#8b5cf6', 'marginBottom': '10px', 'fontSize': '16px'}),
                        html.P('El criterio de optimalidad se cumplió en la iteración 4: todos los costos reducidos son no-positivos, garantizando que no existe mejor solución.',
                              style={'color': colors['text'], 'fontSize': '14px', 'margin': '0', 'lineHeight': '1.6'})
                    ])
                ])
            ])
        ])
    
    # Agregar footer
    content = html.Div([content, create_footer()])
    return content

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(debug=True, mode='inline', port=8050)