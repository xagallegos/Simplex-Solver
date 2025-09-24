import streamlit as st

def main_page():
    
    with st.sidebar:
        st.title("Método Simplex")
        size = st.number_input("Número de variables:", min_value=2, step=1)
        res = st.number_input("Número de restricciones:", min_value=1, step=1)

        st.write("#")

        if st.button("Resolver", type="primary", width="stretch"):
            pass

    st.header("Introduce tu matriz")

    # Función objetivo
    with st.container():
        st.subheader("Función Objetivo")
        
        cols_fo = st.columns([1/(size+2) for _ in range(size)] + [2/(size+2)],
            gap="medium")
        for i, col in enumerate(cols_fo[:-1]):
            with col:
                st.text(f"x{i+1}")
                st.number_input("", value=0, step=1, key=f"fo-x{i+1}", label_visibility="collapsed")
        with cols_fo[-1]:
            st.text("Objetivo")
            st.selectbox("", ["Minimizar", "Maximizar"], label_visibility="collapsed")

    # Restricciones 
    with st.container():
        st.subheader("Restricciones")
        cols_res = st.columns(size+2, gap="medium")

        for i, col in enumerate(cols_res[:-2]):
            with col:
                st.text(f"x{i+1}")
                for r in range(1, res+1):
                    st.number_input("", value=0, step=1, key=f"r{r}-x{i}", label_visibility="collapsed")
            
        with cols_res[-2]:
            st.text("Signo")
            for  r in range(1, res+1):
                st.selectbox("", ["<=", "=", ">="], label_visibility="collapsed", key=f"r{r}-s")
        
        with cols_res[-1]:
            st.text("LD")
            for r in range(1, res+1):
                st.number_input("", value=0, step=1, key=f"r{r}-ld", label_visibility="collapsed")
            

    
st.navigation([st.Page(main_page)]).run()