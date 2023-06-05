from chidata import data


def test_business_license_pagination_100():
    df = data.business_license.get(100)
    assert df.shape == (100, 34)


def test_business_license_pagination_3000():
    df = data.business_license.get(3000)
    assert df.shape == (3000, 34)
