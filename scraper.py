import asyncio
import re
from playwright.async_api import async_playwright

async def get_vacancia(ticker):
    url = f"https://www.fundsexplorer.com.br/funds/{ticker.lower()}"

    print("\n==========================")
    print(f"🔎 {ticker}")
    print(f"🌐 {url}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto(url, timeout=60000)

        # ⏳ esperar gráfico carregar
        await page.wait_for_timeout(8000)

        try:
            # 🔥 pega o textarea do data view
            textarea = await page.query_selector("#vacancia-chart textarea")

            if not textarea:
                print("❌ textarea não encontrado")
                return "N/D"

            content = await textarea.input_value()

            print("\n📄 DATA VIEW:")
            print(content[:300])

            # =========================
            # PEGAR ÚLTIMA LINHA
            # =========================
            linhas = content.strip().split("\n")

            ultima = linhas[-1]

            print(f"\n📊 Última linha: {ultima}")

            # pegar último número (vacância financeira)
            valores = re.findall(r"[0-9]+\.?[0-9]*", ultima)

            if len(valores) >= 4:
                vacancia = valores[-1]
            else:
                vacancia = "N/D"

            print(f"✅ Vacância: {vacancia}")

            await browser.close()
            return vacancia

        except Exception as e:
            print("❌ ERRO:", e)
            await browser.close()
            return "N/D"


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

    for t in tickers:
        await get_vacancia(t)


asyncio.run(main())
