<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
	<!-- <xsl:output method="html" encoding="UTF-8" doctype-system="about:legacy-compat" indent="yes"/> -->
	
	<!-- <xsl:template match="/"> -->
		<!-- <html lang="fr"> -->
			<!-- <head> -->
				<!-- <title>result</title> -->
				<!-- <meta charset="utf-8"/> -->
				<!-- <link href="./css/style.css" type="text/css" rel="stylesheet"/> -->
				<!-- <meta name="viewport" content="width=device-width, initial-scale=1.0"/> -->
			<!-- </head> -->
			<!-- <body> -->
				<!-- <xsl:apply-templates select="resultat"/> -->
			<!-- </body> -->
		<!-- </html> -->
	<!-- </xsl:template> -->
	
    <xsl:template match="resultat">
		<xsl:for-each select="./bloc">
			<h3><xsl:value-of select="./titre"/></h3>
				<xsl:for-each select="./texte">
					<xsl:if test="@src">
						<img src="{@src}" alt="{@src}"/>
					</xsl:if>
					<xsl:for-each select="./paragraphe">
						<p><xsl:value-of select="."/></p>
					</xsl:for-each>
					<xsl:for-each select="./liste">
						<ul><xsl:for-each select="./element">
							<li><xsl:value-of select="."/></li>
						</xsl:for-each></ul><br/>
					</xsl:for-each>
				</xsl:for-each>
		</xsl:for-each>
	</xsl:template>
    
</xsl:stylesheet>