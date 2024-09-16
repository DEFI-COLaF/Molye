<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:tei="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="xs"
    version="2.0">
    <xsl:output method="html" indent="yes" encoding="UTF-8"/>
    <xsl:strip-space elements="*"/>
    
    <!--Base HTML-->
    <xsl:template match="/">
        <xsl:variable name="titre1" select="//tei:fileDesc/tei:titleStmt//tei:title[@type = 'main']"/>
        <xsl:variable name="head">
            <head>
                <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
                <link rel="stylesheet"
                    href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css"
                    integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T"
                    crossorigin="anonymous"/>
                <title>
                    <xsl:value-of select="$titre1"/>
                </title>
                <style>
                    /* Sidebar styles */
                    .sidebar {
                    position: sticky;
                    top: 0;
                    width: 250px;
                    height: 100vh; /* Full height */
                    background-color: #333;
                    padding: 20px;
                    overflow-y: auto;
                    color: white;
                    }
                </style>
                

            </head>
        </xsl:variable>
        <xsl:result-document method="html" indent="yes">
            <html>
                <xsl:copy-of select="$head"/>
                <body>
                    <div class="sidebar">
                        <h2>Menu</h2>
                        <ul>
                            <li><a href="#section1">Section 1</a></li>
                            <li><a href="#section2">Section 2</a></li>
                            <li><a href="#section3">Section 3</a></li>
                            <li><a href="#section4">Section 4</a></li>
                        </ul>
                    </div>
                    
                    <div class="container">
                        <div class="row text-justify" style="margin:50px;align='center'">
                            <div>
                                <!--Affichage des métadonnées-->
                                <h3><xsl:value-of select="$titre1"/></h3>
                                <h4><xsl:value-of select="//tei:bibl[@type='PrintSource']/tei:author"/>, 
                                    <xsl:value-of select=".//tei:bibl[@type='PrintSource']/tei:date/@when"/></h4>
                                <ul class="casting">
                                    <b>ACTEURS</b>
                                    <xsl:apply-templates select=".//tei:listPerson"/>
                                </ul>
                                <ul class="langues">
                                    <b>LANGUES</b>
                                    <xsl:apply-templates select=".//tei:langUsage"/>
                                </ul>
                                <!--Affichage du texte-->
                                <xsl:apply-templates select="//tei:div[@type='act']"/>                        
                            </div>
                        </div>
                    </div>
                    <script>
                        // Get all checkboxes within the "langues" class
                        const checkboxes = document.querySelectorAll('.langues input[type="checkbox"]');
                        
                        // Function to toggle color of paragraphs based on checkbox state
                        function toggleColor(checkbox) {
                        // Get the lang attribute from the checkbox name
                        const lang = checkbox.name;
                        // Select paragraphs that match the lang attribute
                        const paragraphs = document.querySelectorAll(`p[lang="${lang}"]`);
                        paragraphs.forEach(p => {
                        // Toggle the color based on checkbox state
                        p.style.color = checkbox.checked ? 'red' : '';
                        });
                        }
                        
                        // Add event listeners to all checkboxes
                        checkboxes.forEach(checkbox => {
                        checkbox.addEventListener('change', () => toggleColor(checkbox));
                        });
                    </script>
                    <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"/>
                    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"/>
                    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"/>
                </body>
                <!--<xsl:copy-of select="$footer"/>-->
            </html>
        </xsl:result-document>
    </xsl:template>
    <xsl:template match="tei:div[@type='act']">
        <hr/>
        <div class="act">
            <xsl:attribute name="id">
                <xsl:value-of select="@n"/>
            </xsl:attribute>
            <b>ACTE <xsl:value-of select="@n"/>.</b>
            <xsl:apply-templates select="*"/>
        </div>
        
    </xsl:template>
    <xsl:template match="tei:div[@type='scene']">
        <hr/>
        <div class="scene">
            <xsl:attribute name="id">
                <xsl:value-of select="@n"/>
            </xsl:attribute>
            <b><xsl:value-of select="./tei:head"/></b>
            <hr/>
            <xsl:apply-templates select="* except ./tei:head"/>
        </div>
    </xsl:template>
    <xsl:template match="tei:p">
        <xsl:element name="p">
            <xsl:if test='@xml:lang'>
                <xsl:attribute name="lang">
                    <xsl:value-of select="@xml:lang"/>
                </xsl:attribute>
            </xsl:if>
            <xsl:if test="@xml:lang != 'met-fr'">
            </xsl:if>
            <xsl:apply-templates/>
        </xsl:element>
    </xsl:template>
    <xsl:template match="tei:speaker">
        <b><p class="locuteur">
            <xsl:apply-templates/>
        </p></b>
    </xsl:template>
    <xsl:template match="tei:stage">
        <p class="didascalie">
            <i><xsl:apply-templates/></i>
        </p>
    </xsl:template>
    <xsl:template match="tei:l">
        <p class="vers">
            <xsl:if test='@xml:lang'>
                <xsl:attribute name="lang">
                    <xsl:value-of select="@xml:lang"/>
                </xsl:attribute>
            </xsl:if>
            <xsl:apply-templates/>
        </p>
    </xsl:template>
    <xsl:template match="tei:person">
        <li>
            <xsl:value-of select="./tei:persName"/>
        </li>
    </xsl:template>
    <xsl:template match="tei:langUsage">
        <br/>
        <b> Faire apparaître le texte dans le language suivant:</b>
            <xsl:apply-templates select="./tei:language"/>
    </xsl:template>
    <xsl:template match="tei:language">
        <br/>
        <input type="checkbox">
            <xsl:attribute name="id">
                <xsl:value-of select="@ident"/>
            </xsl:attribute>
            <xsl:attribute name="name">
                <xsl:value-of select="@ident"/>
            </xsl:attribute>
            <xsl:value-of select="./tei:name"/>
            <xsl:if test="./tei:date"> (<xsl:value-of select="./tei:date/@when"/>)
            </xsl:if>
        </input>
    </xsl:template>
    
</xsl:stylesheet>