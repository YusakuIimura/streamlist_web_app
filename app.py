import streamlit as st
import pandas as pd
import numpy as np
import os

st.title('Molkky得点管理アプリ')

# セッションステート変数の初期化（current_rowを含む）
if 'page' not in st.session_state:
    st.session_state.page = 'setup'
    st.session_state.current_cell = {'A': 0, 'B': 0, 'C': 0}
    st.session_state.current_row = 0  # ここでcurrent_rowを初期化

if st.session_state.page == 'setup':
    with st.form("setup_form"):
        col1_name = st.text_input("列1の名前", value='col1', key='col1')
        col2_name = st.text_input("列2の名前", value='col2', key='col2')
        col3_name = st.text_input("列3の名前", value='col3', key='col3')
        col4_name = st.text_input("列4の名前", value='col4', key='col4')
        col5_name = st.text_input("列5の名前", value='col5', key='col5')
        col6_name = st.text_input("列6の名前", value='col6', key='col6')
        submitted = st.form_submit_button("列名を設定して得点管理を開始")

    if submitted:
        # 列名をセッションステートに格納
        st.session_state.col_names = [col1_name, col2_name, '計A', col3_name, col4_name, '計B', col5_name, col6_name, '計C']
        st.session_state.page = 'manage_scores'
        # DataFrameの初期化
        custom_index = [f"{i+1}投目" for i in range(15)]

        # DataFrameの初期化時にカスタムインデックスを指定
        st.session_state.df = pd.DataFrame(np.nan, index=custom_index, columns=st.session_state.col_names)
        

elif st.session_state.page == 'manage_scores':
    st.header('得点管理')
    # ここで得点管理の処理を記述
     
    teams = {'A': [st.session_state.col_names[0], st.session_state.col_names[1]], 
             'B': [st.session_state.col_names[3], st.session_state.col_names[4]], 
             'C': [st.session_state.col_names[6], st.session_state.col_names[7]]}
    sum_columns = {'A': '計A', 'B': '計B', 'C': '計C'}
    value_options = [str(i) for i in range(13)] + ['miss']
    
    def check_teams_input_completed():
        # 全チームが現在の行に対して少なくとも一つの得点またはmissを入力したかチェック
        all_teams_completed = True
        for team, cols in teams.items():
            team_input_completed = False
            current_row_label = st.session_state.df.index[st.session_state.current_row]  # 現在の行ラベルを取得
            for col in cols:
                value = st.session_state.df.at[current_row_label, col]  # 行ラベルを使用してアクセス
                if not pd.isna(value) or value == 'miss':  # 'miss'も有効な入力として扱う
                    team_input_completed = True
                    break
            if not team_input_completed:
                all_teams_completed = False
                break
        
        # 全チームが入力を完了した場合、次の行へ移動し、列を交互に切り替える
        if all_teams_completed:
            st.session_state.current_row += 1  # 次の行へのインデックス移動
            for team in teams.keys():
                # 現在の列インデックスを更新して、次の行で交互の列が選択されるようにする
                st.session_state.current_cell[team] = (st.session_state.current_cell[team] + 1) % len(teams[team])
        

    def update_score_and_move_next(team, col, value):
        # 現在の行ラベルを取得
        current_row_label = st.session_state.df.index[st.session_state.current_row]

        # 選択された値を設定
        if value == 'miss':
            st.session_state.df.at[current_row_label, col] = 'miss'
        else:
            st.session_state.df.at[current_row_label, col] = int(value)

        # その行までのセル内の値の総和を計算し、Sum列に累積得点を設定
        for idx, row_label in enumerate(st.session_state.df.index):
            if idx == 0:
                # 初回の得点計算
                st.session_state.df.at[row_label, sum_columns[team]] = st.session_state.df.loc[row_label, teams[team]].apply(pd.to_numeric, errors='coerce').fillna(0).sum()
            else:
                # 以前の累積得点を取得
                prev_label = st.session_state.df.index[idx-1]
                prev_total = st.session_state.df.at[prev_label, sum_columns[team]]
                # 現在の行の得点を加算
                current_total = prev_total + st.session_state.df.loc[row_label, teams[team]].apply(pd.to_numeric, errors='coerce').fillna(0).sum()

                # 累積得点が50を超えた場合の処理
                if current_total > 50:
                    st.session_state.df.at[row_label, sum_columns[team]] = 25
                else:
                    st.session_state.df.at[row_label, sum_columns[team]] = current_total

            check_teams_input_completed()



    # チームごとの得点入力欄を横に並べる
    col_a, col_b, col_c = st.columns(3)
    # 各チームごとに処理
    for team in teams:
        current_col = teams[team][st.session_state.current_cell[team]]
        with {'A': col_a, 'B': col_b, 'C': col_c}[team]:
            st.write(f"チーム{team}: {st.session_state.current_row + 1}行目, {current_col}")
            # カスタムインデックスラベルを取得
            current_index_label = st.session_state.df.index[st.session_state.current_row]

            # カスタムインデックスラベルを使用してセルの値にアクセス
            current_value = st.session_state.df.at[current_index_label, current_col]
            # current_value = st.session_state.df.at[st.session_state.current_row, current_col]
            value_selection = st.selectbox(f'{current_col}の値', value_options, index=value_options.index(str(current_value)) if current_value in value_options else 0, key=f'{team}_{st.session_state.current_row}_{current_col}')

            if st.button(f'Update {team}', key=f'update_{team}_{st.session_state.current_row}'):
                update_score_and_move_next(team, current_col, value_selection)

    # 表の表示
    st.dataframe(st.session_state.df)


    # 間違えた時用の手動修正機能
    st.write("間違えた時の修正")
    selected_team = st.selectbox("チームを選択", list(teams.keys()))
    selected_col = st.selectbox("列名を選択", teams[selected_team])
    row_labels = [f"{i+1}投目" for i in range(len(st.session_state.df))]
    selected_row_label = st.selectbox("行を選択", options=row_labels, index=0)
    value_to_update = st.selectbox("値を選択", value_options)

    if st.button('値をアップデート'):
    # 選択された位置に値を設定
        if value_to_update == 'miss':
            st.session_state.df.at[selected_row_label, selected_col] = 'miss'  # 'miss'を文字列として保存
        else:
            st.session_state.df.at[selected_row_label, selected_col] = int(value_to_update)

        # 各チームの得点を再計算
        for team, cols in teams.items():
            total_score = 0  # チームの累積得点
            for row_label in st.session_state.df.index:
                row_scores = st.session_state.df.loc[row_label, cols].apply(lambda x: 0 if x == 'miss' else pd.to_numeric(x, errors='coerce')).fillna(0)
                row_sum = row_scores.sum()

                # 累積得点の更新
                total_score += row_sum
                if total_score > 50:
                    total_score = 25  # 50を超えたら25にリセット

                st.session_state.df.at[row_label, sum_columns[team]] = total_score

        st.success("値をアップデートしました。")

    # ファイル名の入力
    file_name = st.text_input("保存するファイル名を入力してください", "my_dataframe.csv")

    # 保存パスの設定
    save_path = f"data/{file_name}" 

    # データフレーム保存ボタン
    if st.button('Save DataFrame'):
        # 指定されたファイルが既に存在するかチェック
        if os.path.exists(save_path):
            # ファイルが存在する場合はエラーメッセージを表示
            st.error('Error: The file already exists. Please enter a different file name.')
        else:
            # ファイルが存在しない場合は保存を実行
            st.session_state.df.to_csv(save_path, index=False, encoding="utf-8-sig")
            
            # 保存が完了したことをユーザーに通知
            st.success(f'DataFrame saved to {save_path}')
            # ダウンロードリンクを提供
            st.markdown(f'**Download Link:** [Download {file_name}]("file://{save_path}")')
    
    if st.button('設定ページに戻る'):
        st.session_state.page = 'setup'
