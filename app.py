import streamlit as st
import pandas as pd
import numpy as np
import os

st.title('Molkky得点管理アプリ')

# 列名を個別に入力
col1_name = st.text_input("列1の名前", value='col1')
col2_name = st.text_input("列2の名前", value='col2')
col3_name = st.text_input("列3の名前", value='col3')
col4_name = st.text_input("列4の名前", value='col4')
col5_name = st.text_input("列5の名前", value='col5')
col6_name = st.text_input("列6の名前", value='col6')

if 'current_cell' not in st.session_state:
    st.session_state.current_cell = {'A': 0, 'B': 0, 'C': 0}

# DataFrameの初期化
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(np.nan, index=range(25), columns=[
        col1_name, col2_name, '計A', col3_name, col4_name, '計B', col5_name, col6_name, '計C'
    ])
    st.session_state.current_row = 0

# 値の選択肢
value_options = [str(i) for i in range(13)] + ['miss']

# チームと列のマッピング
teams = {'A': [col1_name, col2_name], 'B': [col3_name, col4_name], 'C': [col5_name, col6_name]}
sum_columns = {'A': '計A', 'B': '計B', 'C': '計C'}

def update_score_and_move_next(team, col, value):
    # 選択された値を設定
    if value == 'miss':
        st.session_state.df.at[st.session_state.current_row, col] = np.nan
    else:
        st.session_state.df.at[st.session_state.current_row, col] = int(value)
    
    # 合計を更新
    sum_col = sum_columns[team]
    st.session_state.df[sum_col] = st.session_state.df[teams[team]].apply(pd.to_numeric, errors='coerce').sum(axis=1)

    # 次のセルに移動
    st.session_state.current_cell[team] = (st.session_state.current_cell[team] + 1) % 2
    if all(st.session_state.current_cell[t] == 0 for t in teams):  # 全チームの列がリセットされたら次の行へ
        st.session_state.current_row += 1

# チームごとの得点入力欄を横に並べる
col_a, col_b, col_c = st.columns(3)

# 各チームごとに処理
for team in teams:
    current_col = teams[team][st.session_state.current_cell[team]]
    with {'A': col_a, 'B': col_b, 'C': col_c}[team]:
        st.write(f"チーム{team}: {st.session_state.current_row + 1}行目, {current_col}")
        current_value = st.session_state.df.at[st.session_state.current_row, current_col]
        value_selection = st.selectbox(f'{current_col}の値', value_options, index=value_options.index(str(current_value)) if current_value in value_options else 0, key=f'{team}_{st.session_state.current_row}_{current_col}')

        if st.button(f'Update {team}', key=f'update_{team}_{st.session_state.current_row}'):
            update_score_and_move_next(team, current_col, value_selection)

# 表の表示
st.dataframe(st.session_state.df)

# 間違えた時用の手動修正機能
st.write("間違えた時の修正")
selected_team = st.selectbox("チームを選択", list(teams.keys()))
selected_col = st.selectbox("列名を選択", teams[selected_team])
selected_row = st.selectbox("行を選択", range(1, 16))
value_to_update = st.selectbox("値を選択", value_options)

if st.button('値をアップデート'):
    # 選択された位置に値を設定
    st.session_state.df.at[selected_row-1, selected_col] = np.nan if value_to_update == 'miss' else int(value_to_update)
    
    # 合計を再計算
    for team, cols in teams.items():
        sum_col = sum_columns[team]
        st.session_state.df[sum_col] = st.session_state.df[cols].apply(pd.to_numeric, errors='coerce').sum(axis=1)
    
    st.success("値をアップデートしました。")

# ファイル名の入力
file_name = st.text_input("保存するファイル名を入力してください", "my_dataframe.csv")

# 保存パスの設定
save_path = f"data/{file_name}"  # 適宜パスを調整

# データフレーム保存ボタン
if st.button('Save DataFrame'):
    # 指定されたファイルが既に存在するかチェック
    if os.path.exists(save_path):
        # ファイルが存在する場合はエラーメッセージを表示
        st.error('Error: The file already exists. Please enter a different file name.')
    else:
        # ファイルが存在しない場合は保存を実行
        st.session_state.df.to_csv(save_path, index=False)
        
        # 保存が完了したことをユーザーに通知
        st.success(f'DataFrame saved to {save_path}')
        # ダウンロードリンクを提供
        st.markdown(f'**Download Link:** [Download {file_name}]("file://{save_path}")')

