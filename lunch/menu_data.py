"""식당 실시간 정보가 아닌, 추천 연습용 메뉴와 대략적인 참고값입니다."""

# id, 한국어, English, cuisine, 식사 예상 분, 참고 원, diet, spicy, emoji, 설명, English description
MENUS = [
    (1, '김밥', 'Gimbap', 'korean', 10, 6000, 'any', 0, '🍙', '한입씩 먹기 좋은 한국식 김밥', 'Korean rice rolls with assorted fillings'),
    (2, '비빔밥', 'Bibimbap', 'korean', 15, 10000, 'any', 1, '🥣', '채소와 밥을 비벼 먹는 든든한 한 그릇', 'A rice bowl with vegetables and mixed toppings'),
    (3, '불고기 덮밥', 'Bulgogi rice bowl', 'korean', 15, 12000, 'any', 0, '🍚', '달콤한 간장 양념 소고기 덮밥', 'Rice topped with sweet soy-marinated beef'),
    (4, '김치찌개', 'Kimchi stew', 'korean', 20, 10000, 'any', 1, '🍲', '김치와 돼지고기를 넣은 얼큰한 찌개', 'Spicy kimchi and pork stew, served with rice'),
    (5, '잔치국수', 'Warm noodle soup', 'korean', 12, 8000, 'any', 0, '🍜', '따뜻한 국물에 담긴 가는 밀국수', 'Thin wheat noodles in a warm broth'),
    (6, '채소 비빔밥', 'Vegetarian bibimbap', 'korean', 15, 10000, 'vegetarian', 1, '🥬', '고기를 빼고 채소와 달걀로 주문하는 비빔밥', 'Vegetables and egg over rice; request no meat'),
    (7, '두부 채소 덮밥', 'Plant-based tofu bowl', 'asian', 15, 11000, 'vegan', 0, '🥗', '두부와 채소, 식물성 소스로 주문하는 덮밥', 'Tofu and vegetables; request plant-based sauce'),
    (8, '가락국수', 'Udon noodle soup', 'japanese', 12, 9000, 'any', 0, '🍜', '굵은 면을 담은 따뜻한 일본식 국수', 'Thick wheat noodles in Japanese-style broth'),
    (9, '돈가스', 'Pork cutlet', 'japanese', 18, 12000, 'any', 0, '🍱', '바삭한 돼지고기 튀김과 밥', 'Crispy breaded pork with rice'),
    (10, '연어 덮밥', 'Salmon rice bowl', 'japanese', 15, 16000, 'any', 0, '🍣', '연어와 밥을 함께 즐기는 한 그릇', 'Salmon served over rice'),
    (11, '치킨 샌드위치', 'Chicken sandwich', 'western', 10, 9000, 'any', 0, '🥪', '닭고기와 신선한 채소를 넣은 샌드위치', 'A sandwich with chicken and fresh vegetables'),
    (12, '치즈 채소 샌드위치', 'Cheese & veggie sandwich', 'western', 10, 8000, 'vegetarian', 0, '🥪', '고기 없이 치즈와 채소를 넣은 샌드위치', 'Cheese and vegetables; request no meat'),
    (13, '병아리콩 샐러드', 'Chickpea salad', 'western', 12, 11000, 'vegan', 0, '🥗', '병아리콩과 채소, 식물성 드레싱으로 주문', 'Chickpeas and greens; request plant-based dressing'),
    (14, '토마토 파스타', 'Tomato pasta', 'western', 20, 14000, 'vegetarian', 0, '🍝', '고기 없는 토마토 소스로 주문하는 파스타', 'Pasta with meat-free tomato sauce'),
    (15, '쌀국수', 'Pho noodle soup', 'asian', 15, 11000, 'any', 0, '🍜', '향긋한 국물과 부드러운 쌀국수', 'Rice noodles in an aromatic broth'),
    (16, '매운 볶음밥', 'Spicy fried rice', 'asian', 15, 10000, 'any', 1, '🍛', '매콤하게 볶아 낸 한 접시', 'A warm plate of spicy stir-fried rice'),
    (17, '채소 랩', 'Plant-based veggie wrap', 'western', 5, 8000, 'vegan', 0, '🌯', '채소와 콩, 식물성 소스로 주문하는 랩', 'Vegetables and beans; request plant-based sauce'),
    (18, '달걀 샌드위치', 'Egg sandwich', 'western', 5, 7000, 'vegetarian', 0, '🥪', '부드러운 달걀을 넣은 간단한 샌드위치', 'A simple sandwich with a soft egg filling'),
]
