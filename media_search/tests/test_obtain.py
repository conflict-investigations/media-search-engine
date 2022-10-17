from media_search import obtain

def test_load_files():
    data = obtain.load_files()
    processed = {}

    reukraine = obtain.process_reukraine(data)

    def add_src(src):
        for key in src.keys():
            if not processed.get(key):
                processed[key] = []
            processed[key].append(src[key])

    add_src(reukraine)

    EXPECTED = [{
        'desc': '19.03.2022 about 20:20 Russian troops fired artillery fire on the territory of Zelenodolsk Krivoy Rog, Dnipropetrovsk region.',
        'id': 'reukraine-1920',
        'location': {'latitude': '47.55674851498328000', 'longitude': '33.65361213684083000', 'place_desc': 'м. Зеленодольськ Криворізького району'},
        'source': 'REUKRAINE',
        'unsanitized_url': 'https://1kr.ua/news-70392.html',
    }]
    assert processed['1kr.ua/news-70392.html'] == EXPECTED
