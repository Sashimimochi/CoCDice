import numpy as np
import pandas as pd
import streamlit as st
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder

from retrying import retry

from collections import Counter

def dice(dice_num, dice_size):
    return np.random.randint(1, int(dice_size), int(dice_num))

class Charactor:
    def __init__(self, LIMIT_POINT, work_chara_type, hobby_chara_type):
        self.LIMIT_POINT = LIMIT_POINT
        self.work_chara_type = work_chara_type
        self.hobby_chara_type = hobby_chara_type
        self.work_peaky = False if work_chara_type == '万能型' else True
        self.hobby_peaky = False if hobby_chara_type == '万能型' else True
        self.MAX_POINT = 10
        self.battle = [
            '回避', 'キック', '組みつき', 'こぶし',
            '頭突き', '投擲', 'マーシャルアーツ',
            '拳銃', 'サブマシンガン', 'ショットガン',
            'マシンガン', 'ライフル', '杖', 'ナイフ']
        self.explorater = [
            '応急手当', '鍵開け', '隠す', '隠れる',
            '聞き耳', '忍び歩き', '写真術', '精神分析',
            '追跡', '登攀', '図書館', '目星']
        self.actions = [
            '運転', '機械修理', '重機械操作',
            '乗馬', '水泳', '制作', '操縦',
            '跳躍', '電気修理', 'ナビゲート',
            '変装']
        self.negotiation = [
            '言いくるめ', '信用', '説得', '値切り', '母国語'
        ]
        self.knowledge = [
           '医学', 'オカルト', '化学', '芸術',
           '経理', '考古学', 'コンピューター',
           '心理学', '生物学', '地質学', '電子工学',
           '天文学', '博物学', '物理学', '法律',
           '薬学', '歴史', '人類学'
        ]

    def charactor_make(self):
        status = {}
        status['STR'] = np.sum(dice(3, 6))
        status['CON'] = np.sum(dice(3, 6))
        status['POW'] = np.sum(dice(3, 6))
        status['DEX'] = np.sum(dice(3, 6))
        status['APP'] = np.sum(dice(3, 6))
        status['SIZ'] = np.sum(dice(2, 6)) + 6
        status['INT'] = np.sum(dice(2, 6)) + 6
        status['EDU'] = np.sum(dice(3, 6)) + 3
        status['年収(万円)'] = np.sum(dice(3, 6)) * 50
        status['財産(万円)'] = status['年収(万円)'] * 5

        for k,v in status.items():
            if  8 <= v and v <= 12:
                correction = np.random.rand()
                if correction > 0.7:
                    new_v = v + np.sum(dice(3, 4))
                    status[k] = new_v if new_v <= 21 else 21
                elif correction < 0.1:
                    new_v = v - np.sum(dice(2, 3))
                    status[k] = new_v if new_v >= 3 else 3
        if status['SIZ'] < 8:
            status['SIZ'] = 8
        if status['INT'] < 8:
            status['INT'] = 8
        if status['EDU'] < 6:
            status['EDU'] = 6

        status['HP((CON+SIZ)÷2)'] = int((status['CON'] + status['SIZ']) / 2)
        status['MP(	POW×1)'] = status['POW']
        status['SAN(POW×5)'] = status['POW'] * 5
        status['アイディア(INT×5)'] = status['INT'] * 5
        status['幸運(POW×5)'] = status['POW'] * 5
        status['知識(EDU×5)'] = status['EDU'] * 5
    
        ATK = (status['STR'] + status['SIZ'])
        if 2 <= ATK and ATK <= 12:
            status['db'] = '-1d6'
        elif 13 <= ATK and ATK <= 16:
            status['db'] = '-1d4'
        elif 17 <= ATK and ATK <= 24:
            status['db'] = '0d0'
        elif 25 <= ATK and ATK <= 32:
            status['db'] = '1d4'
        elif 33 <= ATK and ATK <= 40:
            status['db'] = '1d6'
        elif 41 <= ATK and ATK <= 56:
            status['db'] = '2d6'
        elif 57 <= ATK and ATK <= 72:
            status['db'] = '3d6'

        hobby_points = status['INT'] * 10
        skill_points = status['EDU'] * 20
        status['趣味技能ポイント(INT×10)'] = hobby_points
        status['職業技能ポイント(EDU×20)'] = skill_points

        abilities, allot_skill_points, allot_hobby_points = self.ability_make(status, skill_points, hobby_points)
        data = list(status.values()) + list(abilities.values())
        index = list(status.keys()) + list(abilities.keys())
        allot_skill_points = ['-' for _ in range(len(status.keys()))] + list(allot_skill_points.values())
        allot_hobby_points = ['-' for _ in range(len(status.keys()))] + list(allot_hobby_points.values())
        return pd.DataFrame(data={'Skill': index, 'Point': data, '職業技能': allot_skill_points, '趣味技能': allot_hobby_points})

    def ability_make(self, status, skill_points, hobby_points):
        abilities = dict()
        abilities['回避'] = status['DEX'] * 2
        abilities['こぶし'] = 50
        abilities['キック'] = 25
        abilities['頭突き'] = 10
        abilities['組みつき'] = 25
        abilities['投擲'] = 25
        abilities['マーシャルアーツ'] = 1
        abilities['拳銃'] = 20
        abilities['ライフル'] = 25
        abilities['サブマシンガン'] = 15
        abilities['ショットガン'] = 30
        abilities['マシンガン'] = 15
        abilities['杖'] = 25
        abilities['ナイフ'] = 25
        abilities['応急手当'] = 30
        abilities['鍵開け'] = 1
        abilities['隠す'] = 15
        abilities['隠れる'] = 10
        abilities['写真術'] = 10
        abilities['変装'] = 1
        abilities['機械修理'] = 20
        abilities['電気修理'] = 10
        abilities['制作'] = 5
        abilities['操縦'] = 1
        abilities['運転'] = 20
        abilities['重機械操作'] = 1
        abilities['コンピュータ'] = 1
        abilities['追跡'] = 10
        abilities['登攀'] = 40
        abilities['忍び歩き'] = 10
        abilities['乗馬'] = 5
        abilities['水泳'] = 25
        abilities['跳躍'] = 25
        abilities['経理'] = 10
        abilities['目星'] = 25
        abilities['聞き耳'] = 25
        abilities['ナビゲート'] = 10
        abilities['言いくるめ'] = 5
        abilities['信用'] = 15
        abilities['説得'] = 15
        abilities['値切り'] = 5
        abilities['オカルト'] = 5
        abilities['精神分析'] = 1
        abilities['図書館'] = 25
        abilities['医学'] = 5
        abilities['化学'] = 1
        abilities['考古学'] = 1
        abilities['人類学'] = 1
        abilities['生物学'] = 1
        abilities['地質学'] = 1
        abilities['電子工学'] = 1
        abilities['天文学'] = 1
        abilities['博物学'] = 10
        abilities['物理学'] = 1
        abilities['薬学'] = 1
        abilities['心理学'] = 5
        abilities['法律'] = 5
        abilities['歴史'] = 20
        abilities['クトゥルフ神話'] = 0
        abilities['母国語'] = status['EDU'] * 5
        abilities['芸術'] = 5

        allot_hobby_points = dict()
        allot_skill_points = dict()
        for ab in abilities.keys():
            allot_hobby_points[ab] = 0
            allot_skill_points[ab] = 0
    
        abilities, allot_skill_points = self.allot_points(abilities, allot_skill_points, skill_points, _type='work')
        abilities, allot_hobby_points = self.allot_points(abilities, allot_hobby_points, hobby_points, _type='hobby')

        return abilities, allot_skill_points, allot_hobby_points

    def allot_points(self, abilities, allot_points_list, left_points, _type):
        max_allot_points = left_points
        peaky = self.work_peaky if _type == 'work' else self.hobby_peaky
        selected_abilities = self.select_abilities(int(left_points/self.LIMIT_POINT)+5, _type) if peaky else None
        while left_points > 0:
            skill, point = self.allot_point(abilities, left_points, selected_abilities=selected_abilities)
            abilities[skill] += point
            allot_points_list[skill] += point
            left_points -= point
        assert np.sum(list(allot_points_list.values())) == max_allot_points, f'sum allot points {np.sum(list(allot_points_list.values()))} over max allot points {max_allot_points}'
        return abilities, allot_points_list

    @retry()
    def allot_point(self, abilities, left_points, selected_abilities=None):
        size = left_points if left_points < self.MAX_POINT else self.MAX_POINT
        point = size if size == 1 else np.sum(dice(1, size))
        skill = self.select_skill(abilities, point, selected_abilities=selected_abilities)
        return skill, point

    def select_skill(self, abilities, point, selected_abilities=None):
        skill = np.random.choice(selected_abilities) if selected_abilities else np.random.choice(list(abilities.keys()))
        if point + abilities[skill] <= self.LIMIT_POINT and skill != 'クトゥルフ神話':
            return skill
        print(f'{skill}: {point + abilities[skill]} over {self.LIMIT_POINT}')
        raise Exception()

    def choice_skills(self, skills, size):
        _size = len(skills) if len(skills) <= size else size
        return list(np.random.choice(skills, _size, replace=False))

    def select_abilities(self, dice_size, _type):
        chara_type = self.work_chara_type if _type == 'work' else self.hobby_chara_type
        if chara_type == '戦闘型':
            prob = [0.6, 0.25, 0.05, 0.05, 0.05]
        elif chara_type == '探索型':
            prob = [0.15, 0.4, 0.15, 0.15, 0.15]
        elif chara_type == '行動型':
            prob = [0.1, 0.25, 0.6, 0.04, 0.01]
        elif chara_type == '交渉型':
            prob = [0.01, 0.08, 0.01, 0.6, 0.3]
        elif chara_type == '知識型':
            prob = [0.01, 0.22, 0.05, 0.22, 0.5]
        else:
            prob = [0.2, 0.2, 0.2, 0.2, 0.2]
        assert np.sum(prob) == 1

        c = Counter(np.random.choice(['戦闘系', '探索系', '行動系', '交渉系', '知識系'], size=dice_size, p=prob))
        abilities = []
        abilities += self.choice_skills(self.battle, c['戦闘系'])
        abilities += self.choice_skills(self.explorater, c['探索系'])
        abilities += self.choice_skills(self.actions, c['行動系'])
        abilities += self.choice_skills(self.negotiation, c['交渉系'])
        abilities += self.choice_skills(self.knowledge, c['知識系'])
        return abilities

def main():
    st.title('CoC Character Making Dice')
    st.subheader('6版')
    LIMIT_POINT = st.number_input('ステ振り最大値', min_value= 30, max_value=99, value=90, step=1)
    work_chara_type = st.selectbox(
        '職業ステ振りタイプ',
        ('万能型', '特化型', '戦闘型', '探索型', '行動型', '交渉型', '知識型'))
    hobby_chara_type = st.selectbox(
        '趣味ステ振りタイプ',
        ('万能型', '特化型', '戦闘型', '探索型', '行動型', '交渉型', '知識型'))
    if st.button('Make Character'):
        df = Charactor(LIMIT_POINT, work_chara_type, hobby_chara_type).charactor_make()
        gd = GridOptionsBuilder.from_dataframe(df)
        gd.configure_column('Point', filterable=False, sortable=False, editable=True)
        gridOptions = gd.build()
        AgGrid(df, fit_columns_on_grid_load=True, gridOptions=gridOptions)

if __name__ == '__main__':
    main()
