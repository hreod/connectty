import speedtest
import psutil
import time
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
import plotly.graph_objs as go

# Функция для проверки скорости интернета
def check_internet_speed():
    st = speedtest.Speedtest()
    st.download()
    st.upload()
    results = st.results.dict()

    download_speed = results["download"] / 1_000_000  # Преобразование в Мбит/с
    upload_speed = results["upload"] / 1_000_000  # Преобразование в Мбит/с
    ping = results["ping"]

    return download_speed, upload_speed, ping

# Функция для получения количества активных подключений
def get_active_connections():
    connections = psutil.net_connections()
    active_connections = [conn for conn in connections if conn.status == psutil.CONN_ESTABLISHED]
    return len(active_connections)

# Инициализация Dash приложения
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Internet Speed and Active Connections"),
    dcc.Graph(id='live-update-graph'),
    dcc.Interval(
        id='interval-component',
        interval=10*1000,  # Обновление каждые 10 секунд
        n_intervals=0
    )
])

# Обновление графика в реальном времени
@app.callback(
    Output('live-update-graph', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_graph_live(n):
    download_speed, upload_speed, ping = check_internet_speed()
    active_connections_count = get_active_connections()
    timestamp = time.strftime('%H:%M:%S')

    # Обновление данных
    global download_speeds, upload_speeds, pings, active_connections, timestamps
    download_speeds.append(download_speed)
    upload_speeds.append(upload_speed)
    pings.append(ping)
    active_connections.append(active_connections_count)
    timestamps.append(timestamp)

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=timestamps, y=download_speeds, mode='lines', name='Download Speed (Mbps)', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=timestamps, y=upload_speeds, mode='lines', name='Upload Speed (Mbps)', line=dict(color='green')))
    fig.add_trace(go.Scatter(x=timestamps, y=pings, mode='lines', name='Ping (ms)', line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=timestamps, y=active_connections, mode='lines', name='Active Connections', line=dict(color='red')))

    fig.update_layout(
        title='Internet Speed and Active Connections Over Time',
        xaxis_title='Time',
        yaxis_title='Value',
        template='plotly_dark'
    )

    return fig

# Инициализация глобальных переменных для хранения данных
download_speeds = []
upload_speeds = []
pings = []
active_connections = []
timestamps = []

if __name__ == '__main__':
    app.run_server(debug=True)
