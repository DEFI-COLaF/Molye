<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:tei="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="xs"
    version="1.0">
    <xsl:output method="html" indent="yes" encoding="UTF-8"/>
    <xsl:strip-space elements="*"/>
    
    
    <!--Base HTML pour 1 document XML-->
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
                    body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    margin: 20px;
                    background-color: #f4f4f4;
                    color: #333;
                    }
                    
                    .layout {
                    display: flex;
                    max-width: 1200px;
                    margin: auto;
                    padding: 20px;
                    background-color: #fff;
                    border-radius: 8px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    }
                    
                    .sidebar {
                    width: 30%;
                    padding: 20px;
                    background-color: #d5e8d4;
                    border-right: 2px solid #bdc3c7;
                    padding-right: 30px;
                    }
                    
                    .sidebar b {
                    font-size: 1.2em;
                    color: #2c3e50;
                    }
                    
                    .sidebar p, .sidebar ul {
                    margin: 10px 0;
                    font-size: 1.1em;
                    }
                    
                    .sidebar a {
                    color: #2980b9;
                    text-decoration: none;
                    }
                    
                    .sidebar a:hover {
                    text-decoration: underline;
                    }
                    
                    .content {
                    width: 70%;
                    padding-left: 40px;
                    }
                    
                    h3, h4 {
                    color: #2c3e50;
                    }
                    
                    h3 {
                    font-size: 2em;
                    color: #6aa84f;
                    }
                    
                    h4 {
                    font-size: 1.5em;
                    margin-bottom: 10px;
                    }
                    
                    .row {
                    margin-bottom: 20px;
                    }
                    
                    .locuteur {
                    font-weight: bold;
                    margin-top: 20px;
                    color: #6aa84f;
                    }
                    
                    .content p {
                    font-family: "Georgia", serif;
                    font-size: 1.1em;
                    margin: 5px 0;
                    }
                    
                    .text-justify {
                    text-align: justify;
                    }
                    
                    hr {
                    margin: 20px 0;
                    border: 0;
                    border-top: 1px solid #bdc3c7;
                    }
                    
                    input[type="checkbox"] {
                    margin-right: 5px;
                    }
                </style>
                

            </head>
        </xsl:variable>
            <html>
                <xsl:copy-of select="$head"/>
                <body>
                    <div class="layout">
                    <div class="sidebar">
                        <div>
                            <b>BIBLIOGRAPHIC INFORMATIONS</b>
                            <xsl:call-template name="bibliographic"/>
                        </div>
                        <div class="langues">
                            <b>LANGUAGES</b>
                            <xsl:apply-templates select=".//tei:langUsage"/>
                            </div>
                        <xsl:if test=".//tei:div[@type='act']">
                            <div>
                                <b>MENU</b>
                                <xsl:call-template name="menu"/>
                               </div>
                        </xsl:if>
                    </div>
                    
                    <div class="content">
                        <div class="row text-justify">
                            <div>
                                <!--Affichage des métadonnées-->
                                <h3><xsl:value-of select="$titre1"/></h3>
                                <h4><xsl:value-of select="//tei:bibl[@type='PrintSource']/tei:author"/>, 
                                    <xsl:value-of select=".//tei:bibl[@type='PrintSource']/tei:date/@when"/></h4>
                                <!--Affichage du texte-->
                                <xsl:apply-templates select="//tei:div"/>                        
                            </div>
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
    </xsl:template>
   
   
   
    <xsl:template match="tei:div">
        <hr/>
        <xsl:choose>
            <xsl:when test="@type='act'">
                <div class="act">
                    <xsl:attribute name="id">
                        <xsl:text>act_</xsl:text><xsl:value-of select="@n"/>
                    </xsl:attribute>
                    <xsl:apply-templates select="*"/>
                </div>
            </xsl:when>
            <xsl:when test="@type='scene'">
                <div class="scene">
                    <xsl:attribute name="id">
                        <xsl:text>scene_</xsl:text><xsl:value-of select="@n"/>
                    </xsl:attribute>
                    <xsl:apply-templates select="*"/>
                </div>
            </xsl:when>
            <xsl:when test="@type='chapter'">
                <div class="chapter">
                    <xsl:attribute name="id">
                        <xsl:text>chapter_</xsl:text><xsl:value-of select="@n"/>
                    </xsl:attribute>
                    <xsl:apply-templates select="*"/>
                </div></xsl:when>
            <xsl:otherwise>
                <div>
                    <xsl:apply-templates select="*"/></div>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <xsl:template match="tei:head">
        <b><xsl:value-of select="."/></b>
    </xsl:template>
    
    
    <xsl:template match="tei:p">
        <xsl:element name="p">
            <xsl:if test='@xml:lang'>
                <xsl:attribute name="lang">
                    <xsl:value-of select="@xml:lang"/>
                </xsl:attribute>
            </xsl:if>
            <xsl:apply-templates/>
        </xsl:element>
    </xsl:template>
    <xsl:template match="tei:lg">
        <hr/>
        <xsl:apply-templates select="./tei:l"/>
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
    
    
    
    <xsl:template match="tei:stage">
        <p class="didascalie">
            <i><xsl:apply-templates/></i>
        </p>
    </xsl:template>
    
    <xsl:template match="tei:speaker">
        <b><p class="locuteur">
            <xsl:apply-templates/>
        </p></b>
    </xsl:template>
 
    
    <xsl:template match="tei:list">
        <ul>
        <xsl:for-each select="tei:item">
            <li><xsl:value-of select="."/></li>
        </xsl:for-each>
            </ul>
    </xsl:template>
    <xsl:template match="tei:person">
        <li>
            <xsl:value-of select="./tei:persName"/>
        </li>
    </xsl:template>
    <xsl:template match="tei:langUsage">
        <br/>
            <xsl:apply-templates select="./tei:language"/>
    </xsl:template>
    <xsl:template match="tei:language">
        <input type="checkbox">
            <xsl:attribute name="id">
                <xsl:value-of select="@ident"/>
            </xsl:attribute>
            <xsl:attribute name="name">
                <xsl:value-of select="@ident"/>
            </xsl:attribute>
            
        </input>
            <xsl:value-of select="./tei:name"/>
            <xsl:if test="./tei:date"> (<xsl:value-of select="./tei:date/@when"/>)
            </xsl:if>
        <br/>
    </xsl:template>
    
    <xsl:template name="bibliographic">
        <p>Title: <xsl:value-of select=".//tei:bibl[@type='CorpusSource']/tei:title"/></p>
        <p>Author: <xsl:value-of select=".//tei:bibl[@type='CorpusSource']/tei:author"/></p>
        <p>Publisher:<a>         
            <xsl:attribute name="href">
                <xsl:value-of select=".//tei:bibl[@type='CorpusSource']/tei:ptr/@target"/>
            </xsl:attribute><xsl:value-of select=".//tei:bibl[@type='CorpusSource']/tei:publisher"/></a></p>
        <p>Licence <a href="https://creativecommons.org/licenses/by/4.0/">CC-BY</a></p>
    </xsl:template>
    
    <xsl:template name="menu">
        <xsl:for-each select=".//tei:div[@type='chapter'] | .//tei:div[@type='act']">
        <li><a>
            <xsl:attribute name="href">
                <xsl:choose>
                    <xsl:when test="@type='act'">
                        <xsl:text>#act_</xsl:text>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:text>#chapter</xsl:text>
                    </xsl:otherwise>
                </xsl:choose>
                <xsl:value-of select="@n"/>
            </xsl:attribute>
            <xsl:value-of select="./tei:head"/>
        </a></li>
        </xsl:for-each>
    </xsl:template>
    
    
</xsl:stylesheet>