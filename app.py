import streamlit as st
import pandas as pd
import numpy as np
import os
from PIL import Image

image = Image.open('emc.png')
st.set_page_config(
    page_title='Molkky得点管理アプリ', 
    page_icon=image,)


st.title('Molkky得点管理アプリ')

# セッションステート変数の初期化（current_rowを含む）
if 'page' not in st.session_state:
    st.session_state.page = 'setup'
    st.session_state.current_row = 0

if st.session_state.page == 'setup':
    with st.form("team_member_form"):
        # チーム数とメンバー数の入力（ウィジェットのキーを直接使用）
        num_teams = st.number_input("チーム数を入力してください", min_value=1, value=3, step=1)
        members_per_team = st.number_input("各チームのメンバー数を入力してください", min_value=1, value=2, step=1)
        submit_team_member = st.form_submit_button("次へ")
        st.session_state.num_teams = num_teams
        st.session_state.members_per_team = members_per_team

        if submit_team_member:
            # ウィジェットの値を`st.session_state`から直接使用
            num_teams = st.session_state.num_teams
            members_per_team = st.session_state.members_per_team
            # 次のステップへ移動
            st.session_state.page = 'input_names'

elif st.session_state.page == 'input_names':
    num_teams = st.session_state.num_teams
    members_per_team = st.session_state.members_per_team
    with st.form("names_form"):
        # プレイヤー名の入力フィールドを動的に生成
        player_names = []
        for team_num in range(1, num_teams + 1):
            for member_num in range(1, members_per_team + 1):
                name = st.text_input(f"チーム{team_num}-{member_num}人目の名前", key=f'team{team_num}_member{member_num}')
                player_names.append(name)
        submit_names = st.form_submit_button("列名を設定して得点管理を開始")
        
        if submit_names:
            # プレイヤー名をセッションステートに格納し、列名を生成
            st.session_state.player_names = player_names
            col_names = []
            for i, name in enumerate(player_names, start=1):
                col_names.append(name)
                if i % st.session_state.members_per_team == 0:  # 各チームの最後のメンバー後に合計列を追加
                    col_names.append(f'計{i // st.session_state.members_per_team}')
            
            st.session_state.col_names = col_names
            st.session_state.page = 'manage_scores'
            # DataFrameの初期化
            custom_index = [f"{i+1}投目" for i in range(15)]
            st.session_state.df = pd.DataFrame(np.nan, index=custom_index, columns=st.session_state.col_names)

elif st.session_state.page == 'manage_scores':
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

    st.header(f'{st.session_state.num_teams}チーム　{st.session_state.members_per_team}人戦')
    # ここで得点管理の処理を記述
    
    # チームと列の動的定義
    teams = {f'チーム{i+1}': st.session_state.col_names[i * (st.session_state.members_per_team + 1):(i + 1) * (st.session_state.members_per_team + 1) - 1] for i in range(st.session_state.num_teams)}
    sum_columns = {f'チーム{i+1}': st.session_state.col_names[(i + 1) * (st.session_state.members_per_team + 1) - 1] for i in range(st.session_state.num_teams)}
    value_options = [str(i) for i in range(13)] + ['miss']
    st.session_state.current_cell = {team: 0 for team in teams}

    # チームごとに列を動的に生成
    cols = st.columns(st.session_state.num_teams)

    for idx, (team, team_cols) in enumerate(teams.items()):
        with cols[idx]:
            st.write(f"{team}: {st.session_state.df.index[st.session_state.current_row]}行目")
            for col in team_cols:
                current_index_label = st.session_state.df.index[st.session_state.current_row]
                current_value = st.session_state.df.at[current_index_label, col]
                value_selection = st.selectbox(f'{col}の値', value_options, index=value_options.index(str(current_value)) if current_value in value_options else 0, key=f'{team}_{col}_{st.session_state.current_row}')
                if st.button(f'{col} 得点記入', key=f'update_{team}_{col}_{st.session_state.current_row}'):
                    update_score_and_move_next(team, col, value_selection)

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
