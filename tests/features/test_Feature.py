import T720_featureExtract
import T721_featureExtract_cutTubs


def test_PythonFeature_T720_featureExtract(testdata, tmptestdir):
    T720_featureExtract.Test(testdata, tmptestdir, False, False)


def test_PythonFeature_T721_featureExtract_cutTubs(testdata, tmptestdir):
    T721_featureExtract_cutTubs.Test(testdata, tmptestdir, False, False)
