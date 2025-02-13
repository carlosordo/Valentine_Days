import streamlit as st
import pandas as pd
import altair as alt

# Configuración de la aplicación
st.set_page_config(page_title="My Valentine", layout="wide")
col1,col2 = st.columns([1,3])
with col1:
    st.title("My Valentine")
with col2:
    st.image("Imagen de WhatsApp 2025-02-13 a las 02.07.21_4f72ff19.jpg",width=100)
# Simulación de datos
df = pd.read_csv("base.csv")
df["Fecha"] = pd.to_datetime(df["Fecha"])
emojis = pd.read_csv("emojis.csv")

# Sidebar para navegación
st.sidebar.title("Navegación")
page = st.sidebar.radio("Ir a", ["Parte 1", "Parte 2"])

if page == "Parte 1":
    st.title("Whatsapp Carlos/Dome ✨ Babe")
    st.caption("(Periodo 2023-2024)")
    col1, col2 = st.columns([1, 1])
    
    # Mostrar DataFrame en la izquierda
    with col1:
        st.header("Mensajes por dia")
        mens_dia = df.groupby(["Persona","Fecha"])["Mensaje"].count().reset_index().\
            groupby("Persona")["Mensaje"].agg([("Promedio por dia","mean"),("Minimo por dia","min"),("Maximo por dia","max")])\
            .reset_index()
        mens_dia["Promedio por dia"] = mens_dia["Promedio por dia"].astype(int)
        st.dataframe(mens_dia)
        st.text("Total de mensajes: "+ str(df.shape[0]))
        st.text("Total de dias: "+str(df["Fecha"].nunique()))

        ### Longitud de los mensajes
        longitud_ = df[df["Multimedia"]==0].groupby(["Persona"])["Longitud"].\
            agg([("Long Promedio","mean"),("Long Minima","min"),("Long Maxima","max")]).reset_index()
        longitud_["Long Promedio"] = longitud_["Long Promedio"].round(2)
        st.header("Longitud de los mensajes enviados")
        st.dataframe(longitud_)

        ### Multimedias Enviados
        st.header("Archivos Multimedia")
        multimedia_ = df[df["Multimedia"]==1].groupby("Persona").size().reset_index().rename(columns={0:"Total Enviados"})
        pie_chart = alt.Chart(multimedia_).mark_arc().encode(
            theta="Total Enviados:Q",
            color="Persona:N",
            tooltip=["Persona", "Total Enviados"]
        ).properties(width=400, height=400)
        st.altair_chart(pie_chart, use_container_width=True)
        st.caption("Se incluyen Stickers, Imagen, Video y Audios")
        

    # Mostrar métrica en la derecha
    with col2:
        info_emoji = pd.pivot_table(emojis.groupby(["Emojis","Persona"]).size().reset_index(),index="Emojis",columns="Persona",values=0,fill_value=0).reset_index()
        info_emoji["Total"] = info_emoji["Carlos"]+ info_emoji["Dome ✨ Babe"]
        info_emoji["Carlos"] = info_emoji["Carlos"]/info_emoji["Total"]
        info_emoji["Dome ✨ Babe"] = info_emoji["Dome ✨ Babe"]/info_emoji["Total"]
        info_emoji = info_emoji.sort_values(by="Total",ascending=False).reset_index(drop=True).head(5)
        st.header("Emojis más usados")
        st.dataframe(info_emoji)
        st.text("Mensajes con Emojis por Carlos: " +str(df[df["Emoji"]!=0].groupby("Persona").size()["Carlos"]))
        st.text("Mensajes con Emojis por Dome ✨ Babe: "+ str(df[df["Emoji"]!=0].groupby("Persona").size()["Dome ✨ Babe"]))


        ### Barras de mensajes por sentimientos
        st.header("Sentimientos de los mensajes")
        sentiment_ = df[df["conf"]>=0.75].rename(columns={"sent":"Sentimiento"}).groupby(["Persona","Sentimiento"]).size().reset_index(name="mensajes")
        st.subheader("# Mensajes por persona y sentimiento")
        stacked_bar = alt.Chart(sentiment_).mark_bar().encode(
            x="mensajes:Q",
            y=alt.Y("Persona:N", sort="-x"),
            color="Sentimiento:N",
            tooltip=["Persona", "Sentimiento", "mensajes"]
        ).properties(width=600, height=400)
        st.altair_chart(stacked_bar, use_container_width=True)
        st.caption("Creditos a Huggin faces por permitir usar su modelo para clasificar sentimientos (Proximamente nueva clase categoria 'Horny')")

    ### Recordatorio de musica del recordatorio
    st.header("Música de la semana para recordarte")
    if st.button("Reproducir en Spotify 🎶"):
        st.markdown('<meta http-equiv="refresh" content="0; url=https://open.spotify.com/intl-es/track/2lTm559tuIvatlT1u0JYG2?si=174624d711e04737">', unsafe_allow_html=True)
    st.caption("Me parecio divertido ir a la clase de baile, llevo desde ese día tarareando en la oficina.")

elif page == "Parte 2":
    st.title("Whatsapp Carlos/Dome ✨ Babe")
    st.caption("(Periodo 2023-2024)")
    col1, col2 = st.columns([3, 1])
    
    # Filtro con botón de selección
    categoria = st.sidebar.multiselect("Seleccione Sentimientos a mostrar", ["Neutros","Positivos","Negativos","No Clasificados"])
    if len(categoria)==0:
        filtro = df[['Fecha', 'Hora', 'Persona', 'Mensaje','Multimedia', 'sent', 'Dia']]
    else:
        filtro = df[df["sent"].isin(categoria)][['Fecha', 'Hora', 'Persona', 'Mensaje','Multimedia', 'sent', 'Dia']]
    filtro["mes"] = filtro["Fecha"].dt.month

    # Gráfico de líneas con Altair en la izquierda
    with col1:
        st.header("Actividad del chat")
    
        ### Grafico de linea en altair con los mensajes por mes ###
        act_mes = filtro.groupby("mes").size().reset_index()
        act_mes["Persona"] = "Todos"
        act_mes = pd.concat([act_mes,filtro.groupby(["Persona","mes"]).size().reset_index()])
        act_mes.rename(columns={0:"Mensajes"},inplace=True)
        st.subheader("Total de mensajes x mes")
        line_chart = alt.Chart(act_mes).mark_line().encode(
            x="mes:O",  # Mes en el eje X (ordinal)
            y="Mensajes:Q",  # Número de mensajes en el eje Y
            color="Persona:N",  # Diferenciar líneas por persona
            tooltip=["Persona", "mes", "Mensajes"]
        ).properties(
            width=600,
            height=400,
            title="Mensajes enviados por mes"
        ).interactive()
        
        # Mostrar gráfico en Streamlit
        st.altair_chart(line_chart, use_container_width=True)
        ### Grafico de heatmap en altair con las horas y dias de la semana con mas actividad
        st.subheader("Horarios activos")
        ### heatmap
        filtro["Hora"] = pd.to_datetime(filtro["Hora"])
        filtro["Horario"] = filtro["Hora"].dt.hour
        filtro["Dia"] = pd.Categorical(filtro["Dia"], categories=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], ordered=True)
        # Agrupar por Hora y Día
        act_hora = filtro.groupby(["Fecha","Horario", "Dia"])["Mensaje"].count().reset_index().\
            groupby(["Horario", "Dia"])["Mensaje"].mean().reset_index()
        act_hora["Mensaje"] = act_hora["Mensaje"].round(2)
        # Crear el gráfico de calor (heatmap)
        heatmap = alt.Chart(act_hora).mark_rect().encode(
            x=alt.X("Horario:O", title="Hora del Día"),
            y=alt.Y("Dia:O", title="Día de la Semana", sort=act_hora["Dia"].cat.categories.tolist()),
            color=alt.Color("Mensaje:Q", scale=alt.Scale(domain=[0, 1,2,10 ], range=["#fee8c8", "#fdbb84", "#e34a33", "#b30000"]), title="Cantidad de Mensajes"),
            tooltip=["Dia", "Horario", "Mensaje"]
        ).properties(
            width=600,
            height=400,
            title="Actividad por Hora del Día y Día de la Semana"
        )

        # Mostrar el gráfico en Streamlit
        st.altair_chart(heatmap, use_container_width=True)

    # Gráfico de Seaborn en la derecha
    with col2:
        ### Wordcloud de las palabras categorizadas
        st.header("Foto Favorita")
        st.image("WhatsApp Image 2022-07-04 at 3.43.09 AM.jpeg")
        st.caption("Me dijiste que no era el tipo de foto a enviar a Carmencita pero me parecio tierna. Y pos todavia me gusta")