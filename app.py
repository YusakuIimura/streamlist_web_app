import streamlit as st
import pandas as pd
import numpy as np

st.title('Molkky得点計算アプリ')

# 初期化
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(np.nan, index=range(15), columns=['col1', 'col2'])
    st.session_state.df['Sum'] = np.nan

# 列名の編集
col1_name = st.text_input('Column 1 Name', value=st.session_state.df.columns[0])
col2_name = st.text_input('Column 2 Name', value=st.session_state.df.columns[1])

# 列名の更新
st.session_state.df.columns = [col1_name, col2_name, 'Sum']

# 行と値の選択
row_selection = st.selectbox('Row', range(1, 16), index=0)  # 1から15までの行選択
value_options = [str(i) for i in range(13)] + ['miss']  # 0から12の整数と"miss"を選択肢に追加
value_selection = st.selectbox('Value', value_options, index=0)  # "miss"も含む値選択
col_selection = st.selectbox('Column', [col1_name, col2_name])  # 更新された列名で列選択

# 更新ボタン
if st.button('Update Value'):
    # 選択された位置に値を設定（'miss'の場合はnp.nanを設定）
    if value_selection == 'miss':
        st.session_state.df.at[row_selection-1, col_selection] = np.nan
    else:
        st.session_state.df.at[row_selection-1, col_selection] = int(value_selection)
    
    # 数値のみを対象にした3列目の計算
    filled_values = st.session_state.df[[col1_name, col2_name]].apply(pd.to_numeric, errors='coerce')
    st.session_state.df['Sum'] = filled_values.sum(axis=1).cumsum()

# 表の表示
st.dataframe(st.session_state.df)
