import numpy as np
import streamlit as st
import pandas as pd

def main_page():
    st.set_page_config("Simplex", layout="wide")
    
    with st.sidebar:
        st.title("Simplex Method")
        size = st.number_input("Number of variables:", min_value=2, step=1)
        res = st.number_input("Number of restrictions:", min_value=1, step=1)
        M = st.number_input("M value:", min_value=0, value=1000, step=1000)

        st.write("#")

        if st.button("Solve", type="primary", width="stretch", icon=":material/Keyboard_Arrow_Right:"):
            st.session_state["size"] = size
            st.session_state["res"] = res
            st.session_state["M"] = M
            st.session_state["obj"] = st.session_state["objetivo"]

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
            st.switch_page(st.Page(solve))


    #st.header("Introduce tu matriz")

    # Función objetivo
    with st.container():
        st.subheader("Objective Function")
        
        cols_fo = st.columns([1/(size+2) for _ in range(size)] + [2/(size+2)],
            gap="medium")
        for i, col in enumerate(cols_fo[:-1]):
            with col:
                st.text(f"x{i+1}")
                st.number_input("", value=0, key=f"0-x{i+1}", label_visibility="collapsed")
        with cols_fo[-1]:
            st.text("Objective")
            st.selectbox("", ["Minimize", "Maximize"], label_visibility="collapsed", key="objetivo")

    # Restricciones 
    with st.container():
        st.subheader("Restrictions")
        cols_res = st.columns(size+2, gap="medium")

        for i, col in enumerate(cols_res[:-2]):
            with col:
                st.text(f"x{i+1}")
                for r in range(1, res+1):
                    st.number_input("", value=0, key=f"{r}-x{i+1}", label_visibility="collapsed")
            
        with cols_res[-2]:
            st.text("Signo")
            for  r in range(1, res+1):
                st.selectbox("", ["≤", "=", "≥"], label_visibility="collapsed", key=f"{r}-s")
        
        with cols_res[-1]:
            st.text("LD")
            for r in range(1, res+1):
                st.number_input("", value=0, key=f"{r}-ld", label_visibility="collapsed")
            
def solve():
    st.set_page_config("Simplex Solution", layout="wide")

    with st.sidebar:
        st.title("Simplex Method")
        if st.button("Go Back", icon=":material/Keyboard_Arrow_Left:", type="primary", width="stretch"):
            st.switch_page(st.Page(main_page))

    up = st.container()

    matrix = st.session_state.df.copy()

    # Añadir variables de holgura y artificiales
    for r in range(1, st.session_state.res+1):
        signo = matrix.loc[r, "s"]
        if signo == "≤":
            matrix.loc[r, f"s{r}"] = 1
        elif signo == "=":
            matrix.loc[r, f"a{r}"] = 1
        else:
            matrix.loc[r, f"s{r}"] = -1
            matrix.loc[r, f"a{r}"] = 1

    # Llenar con 0s & quitar signos
    matrix.fillna(0, inplace=True)
    matrix.drop(columns="s", inplace=True)
    #matrix.astype(float)

    # Reordenar columnas
    cols = ["z"] + [c for c in matrix.columns if c not in ["z", "ld"]] + ["ld"]
    matrix = matrix[cols]

    # Multiplicar x -1 si es necesario
    for r in range(st.session_state.res+1):
        if r == 0:
            if st.session_state.obj == "Maximize":
                matrix.loc[r] = matrix.loc[r] * -1
        else:
            if matrix.loc[r, "ld"] < 0:
                matrix.loc[r] = matrix.loc[r] * -1

    # Multiplicar variables artificiales x M
    a_var = []
    for col in matrix.columns:
        if col.startswith("a"):
            matrix.loc[0, col] = matrix[col].max() * st.session_state["M"]
            a_var.append(col[1:])
    

    # New 0
    for a in a_var:
        matrix.loc[0] -=  matrix.loc[int(a)].multiply(st.session_state.M)

    i = 0
    show_iter = st.expander("Show iterations")

    # start gauss-jordan loop
    while matrix.drop(columns=["z", "ld"]).loc[0].min(numeric_only=True) < 0:
        col_i, col_m = show_iter.container().columns([0.2,0.8])
        col_i.text(f"Iter {i}")
        col_m.dataframe(matrix[cols])

        pvt_col = matrix.drop(columns=["z", "ld"]).idxmin(axis="columns")[0]
        matrix.loc[1:, "cruce"] = matrix.loc[1:, "ld"].divide(matrix.loc[1:, pvt_col])
        matrix.loc[matrix.cruce < 0, "cruce"] = np.nan
        pvt_row = matrix.idxmin(numeric_only=True).cruce

        # make pvt = 1
        pvt = matrix.loc[pvt_row, pvt_col]

        if  pvt != 0:
            matrix.loc[pvt_row, cols] /= pvt
        
        prvs = matrix.copy()

        for ec in range(st.session_state.res+1):
            if ec != pvt_row:
                for var in cols:
                    matrix.loc[ec, var] =  prvs.loc[ec, var] - prvs.loc[ec, pvt_col] * prvs.loc[pvt_row, var]
        
        i += 1
        

    if st.session_state.obj == "Minimize":
        matrix.loc[0] *= -1
    

    col_i, col_m = show_iter.container().columns([0.2,0.8])
    col_i.text(f"Iter {i}")
    col_m.dataframe(matrix[cols])

    up.latex(f"Z = {matrix.loc[0,'ld']:.2f}")

    for var in cols[1:-1]:
        if matrix[var].sum() == 1 and matrix[var].max() == 1:
            res_row = matrix[var].idxmax()
            res = matrix.loc[res_row, "ld"]
            up.latex(f"{var[0]}_{var[1:]} = {res:.2f}")


pg = st.navigation([
    st.Page(main_page),
    st.Page(solve)
], position="hidden")

pg.run()