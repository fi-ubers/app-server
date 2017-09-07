SRC = config/doxygen
DOXYGEN_CONFIG = doxygen_config
DOXYGEN_DOCS =  ${CURDIR}/docs
DOC_FOLDER = documentation
document:
	rm -f -r ${CURDIR}/docs/documentation
	@mkdir -p docs/documentation
	doxygen $(SRC)/$(DOXYGEN_CONFIG)

	

