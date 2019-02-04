def test_createSentenceSplitter(self):
        assert helpers.sentenceSplitter()
    def test_getExceptionTerms(self):
        assert self.splitter.getExceptionTerms()
    def test_addExceptionTermsWithoutCaseVariants(self):
        self.splitter.addExceptionTerms("D.D.S.", "D.O.")
        assert ("D.O." in self.splitter.getExceptionTerms())
        assert ("d.o." not in self.splitter.getExceptionTerms())
    def test_addExceptionTermsWithCaseVariants(self):
        self.splitter.addExceptionTerms("D.D.S.", "D.O.",addCaseVariants=True)
        assert ("d.o." in self.splitter.getExceptionTerms())
    def test_deleteExceptionTermsWithoutCaseVariants(self):
        self.splitter.deleteExceptionTerms("M.D.")
        assert ("M.D." not in self.splitter.getExceptionTerms())
        assert ("m.d." in self.splitter.getExceptionTerms())
