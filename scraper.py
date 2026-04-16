import asyncio
import re
from playwright.async_api import async_playwright

async def get_data(ticker):
    ticker_base = ticker.replace("11", "").lower()
    url = f"https://www.meusdividendos.com/fundo-imobiliario/{ticker_base}"

    print("\n==========================")
    print(f"🔎 TICKER: {ticker}")
    print(f"🌐 URL: {url}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto(url, timeout=60000)

        # espera carregar
        await page.wait_for_timeout(6000)

        html = await page.content()

        print("📄 HTML carregado:")
        print(html[:500])

        await browser.close()

    text = re.sub(r"\s+", " ", html)

    vac = re.search(r"Vac[âa]ncia Financeira.*?([0-9]+,[0-9]+)%", text)
    inad = re.search(r"Inadimpl[êe]ncia.*?([0-9]+,[0-9]+)%", text)

    return {
        "vacancia": vac.group(1) if vac else "N/D",
        "inadimplencia": inad.group(1) if inad else "N/D"
    }


async def main():
    tickers = ["xpml11", "mxrf11", "tepp11"]

    """
    TICKERS = ["ADSH","AFHI","AFHF","ATWN","AJFI","ALZC","MTOF","ALZR","AURB","APXM","APXU","AIEC","AVUR","AROA","EIRA","ARTE","ARXD","AZPE","AZPL","AZSG",
    "CEBB","BCRI","BNFS","BTML","BZEL","BPDR","BPLC","BPMW","BBFO","BBFI","BBIG","BBRC","BINR","BFCC","BGRB","BGRJ","BLOG","BLMG","BMLC","BRSE","BCIA","BVAR","CARE",
    "FATN","RTEL","BRCT","BRCD","BRCO","BICE","BIME","BRIM","BRIP","BIPD","BIPE","MCMV","BROF","BETW","LLAO","BTHR","BTHI","BRCR","BTCI","BTLG","BTHF","BPML","BTYU",
    "BTWR","BTSI","CXCO","CRFF","CXRI","CCME","CCVA","CPUR","CPLG","CPOF","CPTS","CPSH","CACR","CBOP","BLCA","CVFL","CNES","CDHY","CTXT","CENU","CFII","CJCT","CLSM",
    "CIXM","CIXF","PDBM","CLIN","CSMC","RENV","IBCR","CVPR","CYCR","CYLD","DAMA","DAYM","ASRF","DLMT","DPRO","DEVA","DAMT","DOVL","EDGE","EMET","EGYR","EQIR","ERCR",
    "ERPA","KEVE","EXES","FLCR","VRTA","VRTM","FTRE","FLMA","EGDB","ELDO","EURO","HYPI","HRES","FIIB","FMOF","OPTM","FRBC","ALMI","FLNR","HLMB","KFOF","DVFF","ANCR",
    "FAED","FCFL","CEOC","FAMB","EDGA","FYTO","HCRI","NSLU","MAXR","PQDP","RBRI","RDIV","RBRR","RECR","RECT","SHDP","TRNT","APXR","BRHT","BRCQ","CXAG","CXCI","CXCE",
    "CXTL","IDUA","LKDV","EDFO","NVHO","GTWR","HBCR","HUCG","HUSC","HOSI","FINF","BLUE","MMPD","MCCI","WTSP","PABY","VTPA","FPNG","VTPL","ESTQ","VPSI","RBRY","PULV",
    "RBRP","RELG","RZTR","ROOF","HOMS","FISC","SAIC","SMRE","SOFF","SPVJ","TGAR","TRCO","TRUE","LVBI","PVBI","VERE","FIVN","VSHO","XPRE","BMLT","FIIC","BSLT","TCIN",
    "GCDL","GSRF","GFDL","GLPF","GLCR","GCRI","GCOI","GZIT","FIGS","GSFI","VXXV","GLOG","ABCP","RCFA","GAME","GARE","HABT","ATCR","HCTB","AERO","HCTR","HCST","HCHG",
    "HAAA","ATSA","HGBL","HGBS","HDEL","FLRP","HJCT","HLOG","HOFC","HDOF","HRDF","HREC","SEED","HPDP","HFOF","YEES","HGIC","HIRE","HILG","HTMX","HSAF","HSLG","HSML",
    "HSRE","HUSI","IVCI","GRUL","ICNE","IMMB","INDE","INLG","INRD","ITIP","ITIT","IBBP","XPIN","IRIM","ICDI","ICRI","ILOG","TMPS","ITRI","JCDB","JCDA","JASC","VJFD",
    "JFLL","JCCJ","JPPA","JSAF","JSRE","JSCR","JTPR","BGS1","KISU","KIVO","KRES","KCRE","KNGR","KGUJ","KLOG","KDLG","KFEN","KNHF","KNHY","KNRE","KNIP","KOIM","KORE",
    "KNPR","KPMR","KPRP","KNRI","KNCR","KNSC","KNUQ","LMAI","LPLP","SLDZ","LRED","LSOI","LSII","LSOP","LRDI","LASC","LIFE","LOFT","MAGM","MAGM","MANA","MMVE","MCLO",
    "MCRE","MXRF","MCEM","MFII","MIDW","MGHT","MGRI","MOSO","SHOP","MOFF","NCRI","NAVT","APTO","EAGL","NEWL","NEWU","NMKS","NVIF","OCRE","ONDA","ARRI","OBAL","FTCE",
    "OUJP","OXRL","PNCR","PNDL","PNLM","PNPR","PNRC","PMIS","VTVI","PQAG","PATA","PATB","PCIP","PATC","HGRE","HGLG","PLAG","PATL","PMLL","HGPO","HGCR","VCRR","HGRU",
    "PSEC","PEMA","PMRL","PRSN","PORD","PLRI","PCAS","PRSV","TSER","FPAB","PBLV","QTZD","RZZV","RZZI","RZZR","RBDS","RSPD","RBIR","RFOF","RBLG","FIIP","RBRD","RBTS",
    "DRIM","MTES","REME","RCFF","RDCI","RDLI","SHIP","RBRL","RBRX","RPRI","RBRK","TOPP","RINV","RCRI","RECD","RMBS","RECM","RBHG","RBHY","RBFY","RBFM","RBOP","RCRB",
    "RBRS","RBVA","RNGO","FRRE","RZAK","RZAT","RZLC","RJDA","SAPI","FISD","SCPF","SEQR","SHPH","SHPP","WPLZ","REIT","SJAU","SOLR","SPTW","SPAF","LTMT","DVLP","DVLT",
    "PMFO","SPGM","SPG2","SPXM","SPXL","SPXG","SPXS","STRX","STYI","SURE","SNEL","SNFF","SNLG","SNME","SNCI","SPMO","TELD","TELM","TEPP","TRBL","NAUI","TRPL","TVOI",
    "TIOM","TVRI","VOTS","TJKB","TORD","TSNC","TCPF","TRXY","TRXF","TRXB","URHF","URPR","VVCO","VVMR","VPPR","VVCR","VVRI","VGRM","VGIR","VGIP","VGII","VGHF","VGRI",
    "BLMO","VCJR","VLJS","VNSS","SALI","VCTH","VSLH","FVPQ","VIDS","VDSV","VCRI","VIUR","VILG","VIMO","VINO","VIOL","VISC","SPDE","WHGR","XLPR","XPCM","XPCI","XPLG",
    "XPML","XPSF","YUFI","ZAGH","GGRC","ZAVC","ZAVI","ZIFI"]
    """

    resultado = {}

    for t in tickers:
        data = await get_data(t)
        resultado[t] = data

    print("\n✅ RESULTADO FINAL:")
    print(resultado)


asyncio.run(main())
