from jinja2 import pass_environment
from pyarrow import null
import streamlit as st
import pandas as pd

def main_page():
    st.set_page_config("Simplex", layout="wide")
    
    with st.sidebar:
        st.title("Método Simplex")
        size = st.number_input("Número de variables:", min_value=2, step=1)
        res = st.number_input("Número de restricciones:", min_value=1, step=1)
        with st.popover("Valor de M:", width="stretch"):
            M = st.number_input("", min_value=0, value=1000, step=1, label_visibility="collapsed")

        st.write("#")

        if st.button("Resolver", type="primary", width="stretch"):
            st.session_state["size"] = size
            st.session_state["res"] = res
            st.session_state["M"] = M

            matrix = pd.DataFrame()
            for ec in range(res+1):
                for x in range(1, size+1):
                    matrix.loc[ec, f"x{x}"] = st.session_state[f"{ec}-x{x}"]
                
                if ec == 0:
                    matrix.loc[ec, "z"] = -1
                    matrix.loc[ec, "ld"] = 0
                else:
                    matrix.loc[ec, "z"] = 0
                    matrix.loc[ec, "s"] = st.session_state[f"{ec}-s"]
                    matrix.loc[ec, "ld"] = st.session_state[f"{ec}-ld"]
            
            st.session_state["df"] = matrix
            st.switch_page(st.Page(show_df))


    #st.header("Introduce tu matriz")

    # Función objetivo
    with st.container():
        st.subheader("Función Objetivo")
        
        cols_fo = st.columns([1/(size+2) for _ in range(size)] + [2/(size+2)],
            gap="medium")
        for i, col in enumerate(cols_fo[:-1]):
            with col:
                st.text(f"x{i+1}")
                st.number_input("", value=0, step=1, key=f"0-x{i+1}", label_visibility="collapsed")
        with cols_fo[-1]:
            st.text("Objetivo")
            st.selectbox("", ["Minimizar", "Maximizar"], label_visibility="collapsed", key="obj")

    # Restricciones 
    with st.container():
        st.subheader("Restricciones")
        cols_res = st.columns(size+2, gap="medium")

        for i, col in enumerate(cols_res[:-2]):
            with col:
                st.text(f"x{i+1}")
                for r in range(1, res+1):
                    st.number_input("", value=0, step=1, key=f"{r}-x{i+1}", label_visibility="collapsed")
            
        with cols_res[-2]:
            st.text("Signo")
            for  r in range(1, res+1):
                st.selectbox("", ["<=", "=", ">="], label_visibility="collapsed", key=f"{r}-s")
        
        with cols_res[-1]:
            st.text("LD")
            for r in range(1, res+1):
                st.number_input("", value=0, step=1, key=f"{r}-ld", label_visibility="collapsed")
            
def show_df():
    for r in range(1, st.session_state.res+1):
        signo = st.session_state.df.loc[r, "s"]
        if signo == "<=":
            st.session_state.df.loc[r, f"s{r}"] = 1
        elif signo == "=":
            st.session_state.df.loc[r, f"a{r}"] = 1
        else:
            st.session_state.df.loc[r, f"s{r}"] = -1
            st.session_state.df.loc[r, f"a{r}"] = 1

    for col in st.session_state.df.columns:
        if col.startswith("a"):
            st.session_state.df.loc[0, col] = st.session_state.df[col].max() * st.session_state["M"]

    st.session_state.df.fillna(0, inplace=True)
    st.dataframe(st.session_state.df)
    
pg = st.navigation([
    st.Page(main_page),
    st.Page(show_df)
], position="hidden")

pg.run()