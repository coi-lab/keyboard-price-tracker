# Project Context
Build a site-wide category web scraper for KBDFans that feeds multiple items into our core engine.

# Tech Stack
Python, Requests, BeautifulSoup (bs4)

# Core Requirements
- Target URL: [https://kbdfans.com/collections/switches?page=1]
- Fetch the HTML and parse it using BeautifulSoup.
- Find the HTML elements that represent the product grid.
- Loop through each product card in the grid to extract:
  1. Item Name
  2. Retail Price
  3. Product Link (append the base domain if it's a relative link)
  4. When finishing looping through all the switches which is 32 different ones, I want pagination which will be found https://kbdfans.com/collections/switches?page=1 through changing this link at the page and incrementing the number by 1. 
- **HTML Context for AI:** [
          <div class="product-detail__detail sticky-element"><div class="product-detail__title-area row">
                    <h1 class="product-detail__title small-title">Cherry MX Black Clear-Top Switches MX1A-61NW Linear Switches</h1>
<!--prime badge group1--> 
			<div class="primeBadges outerprimeb7095715922059-1 prime-d-block prime-d-block primebVariantInventory" style="display: inline-block !important;" data-primeproductsid="7095715922059" data-primebouterclass="prime-d-block" data-primebouterstyle="display: inline-block !important;" data-primebinnerclass="prime-d-inline-block prime-mb-1 prime-mr-1" data-primebinnerstyle="" data-primebgroup="1" data-primebmaxdisplaybadge="10">	
    </div>
                    <div class="product-detail__price product-price" data-price-wrapper="">
                      <span class="product-price__reduced" data-product-price="" data-product-detail-price="">
                        <span class="theme-money large-title" data-gpo-product-unit-price="">$4.20</span>
                      </span><span class="visually-hidden" data-compare-text="">Regular price</span>
                        <span class="tiny-title" data-compare-price=""><span class="product-price__compare theme-money">$6.00</span></span>
                    </div><form method="post" action="/cart/add" id="product-form-template--16956097593483__main7095715922059-installments" accept-charset="UTF-8" class="row ajax-product-form" enctype="multipart/form-data"><input type="hidden" name="form_type" value="product"><input type="hidden" name="utf8" value="✓"><input type="hidden" name="id" value="41284919197835" data-product-secondary-select="">
                      
<input type="hidden" name="product-id" value="7095715922059"><input type="hidden" name="section-id" value="template--16956097593483__main"></form></div>
            
            <div id="shopify-block-AdVlUYk1FajlKQkY3W__9f5e3f65-d3e1-4710-9ebd-7f8fd4779654" class="shopify-block shopify-app-block">
  <script>
    window.imageUploader = window.imageUploader || {};
    window.imageUploader.domain = "kbdfans.myshopify.com";
    window.imageUploader.subscription = {"name":"Standard","updated_at":"2026-04-16T12:05:28+08:00","status":"active","shop_created_at":null,"last_checked_at":"2026-04-24T02:21:49.266Z"};
    window.imageUploader.priceOptions = {"isPriceOptionsEnabled":false};
    window.imageUploader.settings = [{"buttonAppearance":{"border":{"width":0,"color":"#000","radius":0},"label":"Upload","buttonText":"Upload","backgroundColor":"#0693E3","fontColor":"#FFFFFF","bold":true},"messageControl":{"minimumDimensionBeforeUpload":{"type":"ERROR","message":"Photo must have at least {width} px width and {height} px height","duration":5},"minimumDimensionCropping":{"type":"ERROR","message":"Zoom out, the image must be bigger to crop","duration":5},"fileType":{"type":"ERROR","message":"You must upload PNG or JPEG files only","duration":5},"characterLimit":{"type":"ERROR","message":"You have reached character limit in this input","duration":5},"uploadRequired":{"type":"ERROR","message":"You must upload image before adding to cart","duration":5},"customTextRequired":{"type":"ERROR","message":"You must add custom text(s) before adding to cart!","duration":5},"productOptionRequired":{"type":"ERROR","message":"This field cannot be empty","duration":10}},"displayConditions":{"option":"MATCH_ANY","conditions":[{"type":"PRODUCT_TAG","operator":"EQUAL","value":"80% tape mod"}]},"uploadConfig":{"minimumDimension":{"dimension":{"width":2073,"height":709},"option":"REQUIRED"},"imageShape":{"option":"RECTANGLE","isCreateThumbCart":null},"customText":{"option":"NONE","texts":[]},"mask":{"enabled":false,"source":null,"width":null,"height":null},"advanced":{"enabled":false,"shapeDimensionTexts":[]},"orientation":{"enabled":false,"label":"Orientation","landscapeLabel":"Landscape","portraitLabel":"Portrait"},"grid":{"enabled":false,"numberPerRow":4},"autoAddToCart":{"enabled":false,"selectors":[]},"checkoutPrompt":{"enabled":false,"title":null,"btnOk":null,"btnCancel":null},"uploadRequired":true,"autoCrop":false,"addToCartClear":false,"quantitySync":false,"hideOnCheckout":false,"minNumberOfFilesUpload":1,"numberOfFilesUpload":1,"customImageLabel":"Custom Image","isCreateShortenUrl":true},"productOptions":{"optionsList":[]},"extras":{"minimumQuantityDisplay":{"enabled":false,"amount":0},"noCropRestriction":false,"fixHorizontalDisplay":false,"displayFeatured":false},"_id":"62943a8a82be6900040b403b","enabled":false,"name":"Tiger tap mod","cropAppearance":{"buttonText":"Crop","rotateLeftText":"Left","rotateRightText":"Right","title":"Crop your image","autoAddToCartBtnText":"Crop & Add to Cart"}},{"buttonAppearance":{"border":{"width":0,"color":"#000","radius":0},"label":"Upload","buttonText":"Upload","backgroundColor":"#0693E3","fontColor":"#FFFFFF","bold":true},"messageControl":{"minimumDimensionBeforeUpload":{"type":"ERROR","message":"Photo must have at least {width} px width and {height} px height","duration":5},"minimumDimensionCropping":{"type":"ERROR","message":"Zoom out, the image must be bigger to crop","duration":5},"fileType":{"type":"ERROR","message":"You must upload PNG or JPEG files only","duration":5},"characterLimit":{"type":"ERROR","message":"You have reached character limit in this input","duration":5},"uploadRequired":{"type":"ERROR","message":"You must upload image before adding to cart","duration":5},"customTextRequired":{"type":"ERROR","message":"You must add custom text(s) before adding to cart!","duration":5},"productOptionRequired":{"type":"ERROR","message":"This field cannot be empty","duration":10}},"displayConditions":{"option":"MATCH_ANY","conditions":[{"type":"PRODUCT_TAG","operator":"EQUAL","value":"75% tape mod"}]},"uploadConfig":{"minimumDimension":{"dimension":{"width":1818,"height":684},"option":"REQUIRED"},"imageShape":{"option":"RECTANGLE"},"customText":{"option":"NONE","texts":[]},"mask":{"enabled":false,"source":null,"width":null,"height":null},"advanced":{"enabled":false,"shapeDimensionTexts":[]},"orientation":{"enabled":false,"label":"Orientation","landscapeLabel":"Landscape","portraitLabel":"Portrait"},"grid":{"enabled":false,"numberPerRow":1},"autoAddToCart":{"enabled":false,"selectors":[]},"uploadRequired":true,"autoCrop":false,"addToCartClear":false,"quantitySync":false,"hideOnCheckout":false,"minNumberOfFilesUpload":1,"numberOfFilesUpload":1,"customImageLabel":"Custom Image"},"productOptions":{"optionsList":[]},"extras":{"minimumQuantityDisplay":{"enabled":false,"amount":0},"noCropRestriction":false,"fixHorizontalDisplay":false,"displayFeatured":false},"_id":"62a1a9e16382620004b0887c","enabled":true,"name":"75% Tape mod customized","cropAppearance":{"buttonText":"Crop","rotateLeftText":"Left","rotateRightText":"Right","title":"Crop your image","autoAddToCartBtnText":"Crop & Add to Cart"}},{"buttonAppearance":{"border":{"width":0,"color":"#000","radius":0},"label":"Upload","buttonText":"Upload","backgroundColor":"#0693E3","fontColor":"#FFFFFF","bold":true},"messageControl":{"minimumDimensionBeforeUpload":{"type":"ERROR","message":"Photo must have at least {width} px width and {height} px height","duration":5},"minimumDimensionCropping":{"type":"ERROR","message":"Zoom out, the image must be bigger to crop","duration":5},"fileType":{"type":"ERROR","message":"You must upload PNG or JPEG files only","duration":5},"characterLimit":{"type":"ERROR","message":"You have reached character limit in this input","duration":5},"uploadRequired":{"type":"ERROR","message":"You must upload image before adding to cart","duration":5},"customTextRequired":{"type":"ERROR","message":"You must add custom text(s) before adding to cart!","duration":5},"productOptionRequired":{"type":"ERROR","message":"This field cannot be empty","duration":10}},"displayConditions":{"option":"MATCH_ANY","conditions":[{"type":"PRODUCT_TAG","operator":"EQUAL","value":"68% tape mod"}]},"uploadConfig":{"minimumDimension":{"dimension":{"width":1818,"height":568},"option":"REQUIRED"},"imageShape":{"option":"RECTANGLE"},"customText":{"option":"NONE","texts":[]},"mask":{"enabled":false,"source":null,"width":null,"height":null},"advanced":{"enabled":false,"shapeDimensionTexts":[]},"orientation":{"enabled":false,"label":"Orientation","landscapeLabel":"Landscape","portraitLabel":"Portrait"},"grid":{"enabled":false,"numberPerRow":1},"autoAddToCart":{"enabled":false,"selectors":[]},"uploadRequired":true,"autoCrop":false,"addToCartClear":false,"quantitySync":false,"hideOnCheckout":false,"minNumberOfFilesUpload":1,"numberOfFilesUpload":1,"customImageLabel":"Custom Image"},"productOptions":{"optionsList":[]},"extras":{"minimumQuantityDisplay":{"enabled":false,"amount":0},"noCropRestriction":false,"fixHorizontalDisplay":false,"displayFeatured":false},"_id":"62a1b7646382620004b08dac","enabled":true,"name":"68% Tape mod customized","cropAppearance":{"buttonText":"Crop","rotateLeftText":"Left","rotateRightText":"Right","title":"Crop your image","autoAddToCartBtnText":"Crop & Add to Cart"}},{"buttonAppearance":{"border":{"width":0,"color":"#000","radius":0},"label":"Upload","buttonText":"Upload","backgroundColor":"#0693E3","fontColor":"#FFFFFF","bold":true},"messageControl":{"minimumDimensionBeforeUpload":{"type":"ERROR","message":"Photo must have at least {width} px width and {height} px height","duration":5},"minimumDimensionCropping":{"type":"ERROR","message":"Zoom out, the image must be bigger to crop","duration":5},"fileType":{"type":"ERROR","message":"You must upload PNG or JPEG files only","duration":5},"characterLimit":{"type":"ERROR","message":"You have reached character limit in this input","duration":5},"uploadRequired":{"type":"ERROR","message":"You must upload image before adding to cart","duration":5},"customTextRequired":{"type":"ERROR","message":"You must add custom text(s) before adding to cart!","duration":5},"productOptionRequired":{"type":"ERROR","message":"This field cannot be empty","duration":10}},"displayConditions":{"option":"MATCH_ANY","conditions":[{"type":"PRODUCT_TAG","operator":"EQUAL","value":"60% tape mod"}]},"uploadConfig":{"minimumDimension":{"dimension":{"width":1692,"height":568},"option":"REQUIRED"},"imageShape":{"option":"RECTANGLE"},"customText":{"option":"NONE","texts":[]},"mask":{"enabled":false,"source":null,"width":null,"height":null},"advanced":{"enabled":false,"shapeDimensionTexts":[]},"orientation":{"enabled":false,"label":"Orientation","landscapeLabel":"Landscape","portraitLabel":"Portrait"},"grid":{"enabled":false,"numberPerRow":1},"autoAddToCart":{"enabled":false,"selectors":[]},"uploadRequired":true,"autoCrop":false,"addToCartClear":false,"quantitySync":false,"hideOnCheckout":false,"minNumberOfFilesUpload":1,"numberOfFilesUpload":1,"customImageLabel":"Custom Image"},"productOptions":{"optionsList":[]},"extras":{"minimumQuantityDisplay":{"enabled":false,"amount":0},"noCropRestriction":false,"fixHorizontalDisplay":false,"displayFeatured":false},"_id":"62a3f16f683d400004f670b1","enabled":true,"name":"60% Tape mod customized","cropAppearance":{"buttonText":"Crop","rotateLeftText":"Left","rotateRightText":"Right","title":"Crop your image","autoAddToCartBtnText":"Crop & Add to Cart"}},{"buttonAppearance":{"border":{"width":0,"color":"#000","radius":0},"label":"Upload","buttonText":"Upload","backgroundColor":"#0693E3","fontColor":"#FFFFFF","bold":true},"messageControl":{"minimumDimensionBeforeUpload":{"type":"ERROR","message":"Photo must have at least {width} px width and {height} px height","duration":5},"minimumDimensionCropping":{"type":"ERROR","message":"Zoom out, the image must be bigger to crop","duration":5},"fileType":{"type":"ERROR","message":"You must upload PNG or JPEG files only","duration":5},"characterLimit":{"type":"ERROR","message":"You have reached character limit in this input","duration":5},"uploadRequired":{"type":"ERROR","message":"You must upload image before adding to cart","duration":5},"customTextRequired":{"type":"ERROR","message":"You must add custom text(s) before adding to cart!","duration":5},"productOptionRequired":{"type":"ERROR","message":"This field cannot be empty","duration":10}},"displayConditions":{"option":"MATCH_ANY","conditions":[{"type":"PRODUCT_TAG","operator":"EQUAL","value":"80% tape mod"}]},"uploadConfig":{"minimumDimension":{"dimension":{"width":2073,"height":709},"option":"REQUIRED"},"imageShape":{"option":"RECTANGLE","isCreateThumbCart":null},"customText":{"option":"NONE","texts":[]},"mask":{"enabled":false,"source":null,"width":null,"height":null},"advanced":{"enabled":false,"shapeDimensionTexts":[]},"orientation":{"enabled":false,"label":"Orientation","landscapeLabel":"Landscape","portraitLabel":"Portrait"},"grid":{"enabled":false,"numberPerRow":4},"autoAddToCart":{"enabled":false,"selectors":[]},"checkoutPrompt":{"enabled":false,"title":null,"btnOk":null,"btnCancel":null},"uploadRequired":true,"autoCrop":false,"addToCartClear":false,"quantitySync":false,"hideOnCheckout":false,"minNumberOfFilesUpload":1,"numberOfFilesUpload":1,"customImageLabel":"Custom Image","isCreateShortenUrl":true},"productOptions":{"optionsList":[]},"extras":{"minimumQuantityDisplay":{"enabled":false,"amount":0},"noCropRestriction":false,"fixHorizontalDisplay":false,"displayFeatured":false},"_id":"64018a8486fc950002505501","enabled":true,"name":"80% Tape mod customized","cropAppearance":{"buttonText":"Crop","rotateLeftText":"Left","rotateRightText":"Right","title":"Crop your image","autoAddToCartBtnText":"Crop & Add to Cart"}},{"buttonAppearance":{"border":{"width":0,"color":"#000","radius":0},"label":"Upload","buttonText":"Upload Tape Mod image","backgroundColor":"#0693E3","fontColor":"#FFFFFF","bold":true},"messageControl":{"minimumDimensionBeforeUpload":{"type":"ERROR","message":"Photo must have at least {width} px width and {height} px height","duration":5},"minimumDimensionCropping":{"type":"ERROR","message":"Zoom out, the image must be bigger to crop","duration":5},"fileType":{"type":"ERROR","message":"You must upload PNG or JPEG files only","duration":5},"characterLimit":{"type":"ERROR","message":"You have reached character limit in this input","duration":5},"uploadRequired":{"type":"ERROR","message":"You must upload image before adding to cart","duration":5},"customTextRequired":{"type":"ERROR","message":"You must add custom text(s) before adding to cart!","duration":5},"productOptionRequired":{"type":"ERROR","message":"This field cannot be empty","duration":10}},"displayConditions":{"option":"MATCH_ANY","conditions":[{"type":"PRODUCT_TITLE","operator":"EQUAL","value":"Holy80 Case"},{"type":"PRODUCT_TITLE","operator":"EQUAL","value":"Holy80 Accessories"}]},"uploadConfig":{"minimumDimension":{"dimension":{"width":2073,"height":749},"option":"REQUIRED"},"imageShape":{"option":"RECTANGLE","isCreateThumbCart":null},"customText":{"option":"NONE","texts":[]},"mask":{"enabled":false,"source":null,"width":null,"height":null},"advanced":{"enabled":false,"shapeDimensionTexts":[]},"orientation":{"enabled":false,"label":"Orientation","landscapeLabel":"Landscape","portraitLabel":"Portrait"},"grid":{"enabled":false,"numberPerRow":4},"autoAddToCart":{"enabled":false,"selectors":[]},"checkoutPrompt":{"enabled":false,"title":null,"btnOk":null,"btnCancel":null},"uploadRequired":true,"autoCrop":false,"addToCartClear":false,"quantitySync":false,"hideOnCheckout":false,"minNumberOfFilesUpload":1,"numberOfFilesUpload":1,"customImageLabel":"Custom Image","isCreateShortenUrl":true},"productOptions":{"optionsList":[]},"extras":{"minimumQuantityDisplay":{"enabled":false,"amount":0},"noCropRestriction":false,"fixHorizontalDisplay":false,"displayFeatured":false},"_id":"6851096eacffb2d6972d2987","enabled":false,"name":"Holy80 Tape mod customized","cropAppearance":{"buttonText":"Crop","rotateLeftText":"Left","rotateRightText":"Right","title":"Crop your image","autoAddToCartBtnText":"Crop & Add to Cart"},"isPriceOptionsEnabled":false}];
  </script>

  
    <script>
      window.imageUploader.meta = {};
      window.imageUploader.meta.product = {"id":7095715922059,"title":"Cherry MX Black Clear-Top Switches MX1A-61NW Linear Switches","handle":"cherry-mx-black-clear-top-switches-mx1a-61nw-linear-switches","description":"\u003cp data-mce-fragment=\"1\"\u003e\u003cstrong\u003eSpecs :\u003c\/strong\u003e\u003c\/p\u003e\n\u003cul\u003e\n\u003cli\u003eMX1A-61NW\u003c\/li\u003e\n\u003cli\u003e\u003cspan\u003eLinear\u003c\/span\u003e\u003c\/li\u003e\n\u003cli\u003e\u003cspan\u003e5-pin, PCB mount\u003c\/span\u003e\u003c\/li\u003e\n\u003cli\u003e\u003cspan\u003eLubricant: Not applied\u003c\/span\u003e\u003c\/li\u003e\n\u003cli\u003eSwitch Type: MX Mechanical Switch\u003c\/li\u003e\n\u003cli\u003eFastening: Fixation Pins in printed circuit board\u003c\/li\u003e\n\u003cli\u003eProtection class: IP40\u003c\/li\u003e\n\u003cli\u003eSwitching voltage: 5V\u003c\/li\u003e\n\u003cli\u003eDielectric strength: 500V \/ 50Hz\u003c\/li\u003e\n\u003cli\u003eDurability: \u0026gt; 50 million actuations\u003c\/li\u003e\n\u003cli\u003eContact configuration: Single-pole contact\u003c\/li\u003e\n\u003cli\u003eActuator travel: 4 mm\u003c\/li\u003e\n\u003cli\u003ePretravel: 2 mm\u003c\/li\u003e\n\u003cli\u003eInitial force: 40cN min.\u003c\/li\u003e\n\u003cli\u003eActuation force: 63,5cN\u003c\/li\u003e\n\u003cli\u003eBounce time: \u0026lt; 1ms\u003c\/li\u003e\n\u003cli\u003eMinimum lead spacing: 16 mm\u003c\/li\u003e\n\u003cli\u003eLighting: Prepared for use with 2-Pin LED (THT, through hole)\u003c\/li\u003e\n\u003cli\u003eInsulation materials: Thermoplastics\u003c\/li\u003e\n\u003cli\u003eSpring: Gold colored, stainless steel\u003c\/li\u003e\n\u003cli\u003eContacts: High-quality gold alloy\u003c\/li\u003e\n\u003cli\u003e10 PCS Per Package\u003c\/li\u003e\n\u003cli\u003eManufacturer: Cherry\u003c\/li\u003e\n\u003c\/ul\u003e\n\u003cp\u003e\u003cimg alt=\"\" src=\"https:\/\/cdn.shopify.com\/s\/files\/1\/1473\/3902\/files\/MX1A-61NW_4d7b8a74-1043-4d1f-830e-87aefa3655e1_480x480.jpg?v=1685425668\"\u003e\u003c\/p\u003e\n\u003cul\u003e\u003c\/ul\u003e\n\u003cp\u003e\u003ca title=\"CHERRY MX Black Clear-Top MX1A-61NW\" href=\"https:\/\/drive.google.com\/file\/d\/1J0tUKkWraNdASE6sCaOHisIP2Vqeetmn\/view?usp=share_link\" target=\"_blank\"\u003e\u003cspan style=\"color: #2b00ff;\"\u003e\u003cstrong\u003eCHERRY MX Black Clear-Top MX1A-61NW\u003c\/strong\u003e\u003c\/span\u003e\u003c\/a\u003e\u003c\/p\u003e","published_at":"2023-03-26T13:41:26+08:00","created_at":"2023-02-27T16:07:22+08:00","vendor":"Cherry","type":"Linear","tags":["10 switches per pack","2025 Summer","2025spr","30% off","Accessories","BFCM2025","on-sale"],"price":420,"price_min":420,"price_max":420,"available":true,"price_varies":false,"compare_at_price":600,"compare_at_price_min":600,"compare_at_price_max":600,"compare_at_price_varies":false,"variants":[{"id":41284919197835,"title":"Default Title","option1":"Default Title","option2":null,"option3":null,"sku":"ZH10371","requires_shipping":true,"taxable":true,"featured_image":null,"available":true,"name":"Cherry MX Black Clear-Top Switches MX1A-61NW Linear Switches","public_title":null,"options":["Default Title"],"price":420,"weight":80,"compare_at_price":600,"inventory_quantity":82,"inventory_management":"shopify","inventory_policy":"deny","barcode":"","requires_selling_plan":false,"selling_plan_allocations":[],"quantity_rule":{"min":1,"max":null,"increment":1}}],"images":["\/\/kbdfans.com\/cdn\/shop\/products\/1_66b4db7d-a8ac-46b7-8686-aff540843f89.jpg?v=1677486850","\/\/kbdfans.com\/cdn\/shop\/products\/2_88069b4c-c640-4dca-b045-3bad1925e9d9.jpg?v=1677486849","\/\/kbdfans.com\/cdn\/shop\/products\/3_a34d6832-428f-4b10-8b60-cd207fc32e45.jpg?v=1677486849","\/\/kbdfans.com\/cdn\/shop\/products\/4_9aa0d49b-e9e0-4790-915a-9a1bbf2a99ee.jpg?v=1677486849","\/\/kbdfans.com\/cdn\/shop\/products\/5_55581aef-fc92-4ec3-a79a-48948fed0f0b.jpg?v=1677486850","\/\/kbdfans.com\/cdn\/shop\/files\/MX1A-61NW.jpg?v=1685425627"],"featured_image":"\/\/kbdfans.com\/cdn\/shop\/products\/1_66b4db7d-a8ac-46b7-8686-aff540843f89.jpg?v=1677486850","options":["Title"],"media":[{"alt":null,"id":24318632034443,"position":1,"preview_image":{"aspect_ratio":1.0,"height":2000,"width":2000,"src":"\/\/kbdfans.com\/cdn\/shop\/products\/1_66b4db7d-a8ac-46b7-8686-aff540843f89.jpg?v=1677486850"},"aspect_ratio":1.0,"height":2000,"media_type":"image","src":"\/\/kbdfans.com\/cdn\/shop\/products\/1_66b4db7d-a8ac-46b7-8686-aff540843f89.jpg?v=1677486850","width":2000},{"alt":null,"id":24318632067211,"position":2,"preview_image":{"aspect_ratio":1.0,"height":2000,"width":2000,"src":"\/\/kbdfans.com\/cdn\/shop\/products\/2_88069b4c-c640-4dca-b045-3bad1925e9d9.jpg?v=1677486849"},"aspect_ratio":1.0,"height":2000,"media_type":"image","src":"\/\/kbdfans.com\/cdn\/shop\/products\/2_88069b4c-c640-4dca-b045-3bad1925e9d9.jpg?v=1677486849","width":2000},{"alt":null,"id":24318632099979,"position":3,"preview_image":{"aspect_ratio":1.0,"height":2000,"width":2000,"src":"\/\/kbdfans.com\/cdn\/shop\/products\/3_a34d6832-428f-4b10-8b60-cd207fc32e45.jpg?v=1677486849"},"aspect_ratio":1.0,"height":2000,"media_type":"image","src":"\/\/kbdfans.com\/cdn\/shop\/products\/3_a34d6832-428f-4b10-8b60-cd207fc32e45.jpg?v=1677486849","width":2000},{"alt":null,"id":24318632132747,"position":4,"preview_image":{"aspect_ratio":1.0,"height":2000,"width":2000,"src":"\/\/kbdfans.com\/cdn\/shop\/products\/4_9aa0d49b-e9e0-4790-915a-9a1bbf2a99ee.jpg?v=1677486849"},"aspect_ratio":1.0,"height":2000,"media_type":"image","src":"\/\/kbdfans.com\/cdn\/shop\/products\/4_9aa0d49b-e9e0-4790-915a-9a1bbf2a99ee.jpg?v=1677486849","width":2000},{"alt":null,"id":24318632165515,"position":5,"preview_image":{"aspect_ratio":1.0,"height":2000,"width":2000,"src":"\/\/kbdfans.com\/cdn\/shop\/products\/5_55581aef-fc92-4ec3-a79a-48948fed0f0b.jpg?v=1677486850"},"aspect_ratio":1.0,"height":2000,"media_type":"image","src":"\/\/kbdfans.com\/cdn\/shop\/products\/5_55581aef-fc92-4ec3-a79a-48948fed0f0b.jpg?v=1677486850","width":2000},{"alt":null,"id":24784207675531,"position":6,"preview_image":{"aspect_ratio":1.0,"height":1800,"width":1800,"src":"\/\/kbdfans.com\/cdn\/shop\/files\/MX1A-61NW.jpg?v=1685425627"},"aspect_ratio":1.0,"height":1800,"media_type":"image","src":"\/\/kbdfans.com\/cdn\/shop\/files\/MX1A-61NW.jpg?v=1685425627","width":1800}],"requires_selling_plan":false,"selling_plan_groups":[],"content":"\u003cp data-mce-fragment=\"1\"\u003e\u003cstrong\u003eSpecs :\u003c\/strong\u003e\u003c\/p\u003e\n\u003cul\u003e\n\u003cli\u003eMX1A-61NW\u003c\/li\u003e\n\u003cli\u003e\u003cspan\u003eLinear\u003c\/span\u003e\u003c\/li\u003e\n\u003cli\u003e\u003cspan\u003e5-pin, PCB mount\u003c\/span\u003e\u003c\/li\u003e\n\u003cli\u003e\u003cspan\u003eLubricant: Not applied\u003c\/span\u003e\u003c\/li\u003e\n\u003cli\u003eSwitch Type: MX Mechanical Switch\u003c\/li\u003e\n\u003cli\u003eFastening: Fixation Pins in printed circuit board\u003c\/li\u003e\n\u003cli\u003eProtection class: IP40\u003c\/li\u003e\n\u003cli\u003eSwitching voltage: 5V\u003c\/li\u003e\n\u003cli\u003eDielectric strength: 500V \/ 50Hz\u003c\/li\u003e\n\u003cli\u003eDurability: \u0026gt; 50 million actuations\u003c\/li\u003e\n\u003cli\u003eContact configuration: Single-pole contact\u003c\/li\u003e\n\u003cli\u003eActuator travel: 4 mm\u003c\/li\u003e\n\u003cli\u003ePretravel: 2 mm\u003c\/li\u003e\n\u003cli\u003eInitial force: 40cN min.\u003c\/li\u003e\n\u003cli\u003eActuation force: 63,5cN\u003c\/li\u003e\n\u003cli\u003eBounce time: \u0026lt; 1ms\u003c\/li\u003e\n\u003cli\u003eMinimum lead spacing: 16 mm\u003c\/li\u003e\n\u003cli\u003eLighting: Prepared for use with 2-Pin LED (THT, through hole)\u003c\/li\u003e\n\u003cli\u003eInsulation materials: Thermoplastics\u003c\/li\u003e\n\u003cli\u003eSpring: Gold colored, stainless steel\u003c\/li\u003e\n\u003cli\u003eContacts: High-quality gold alloy\u003c\/li\u003e\n\u003cli\u003e10 PCS Per Package\u003c\/li\u003e\n\u003cli\u003eManufacturer: Cherry\u003c\/li\u003e\n\u003c\/ul\u003e\n\u003cp\u003e\u003cimg alt=\"\" src=\"https:\/\/cdn.shopify.com\/s\/files\/1\/1473\/3902\/files\/MX1A-61NW_4d7b8a74-1043-4d1f-830e-87aefa3655e1_480x480.jpg?v=1685425668\"\u003e\u003c\/p\u003e\n\u003cul\u003e\u003c\/ul\u003e\n\u003cp\u003e\u003ca title=\"CHERRY MX Black Clear-Top MX1A-61NW\" href=\"https:\/\/drive.google.com\/file\/d\/1J0tUKkWraNdASE6sCaOHisIP2Vqeetmn\/view?usp=share_link\" target=\"_blank\"\u003e\u003cspan style=\"color: #2b00ff;\"\u003e\u003cstrong\u003eCHERRY MX Black Clear-Top MX1A-61NW\u003c\/strong\u003e\u003c\/span\u003e\u003c\/a\u003e\u003c\/p\u003e"};
      window.imageUploader.meta.collections = [{"id":286583423115,"handle":"2024-cny","title":"2024 CNY","updated_at":"2026-05-24T10:26:43+08:00","body_html":"","published_at":"2024-01-31T15:18:32+08:00","sort_order":"best-selling","template_suffix":"","disjunctive":false,"rules":[{"column":"tag","relation":"equals","condition":"on-sale"},{"column":"variant_inventory","relation":"greater_than","condition":"0"}],"published_scope":"web"},{"id":299770019979,"handle":"2025-special-spring-sale-30-off","title":"2025 Special Spring Sale 30% off","updated_at":"2026-05-16T19:01:25+08:00","body_html":"","published_at":"2025-04-08T19:33:16+08:00","sort_order":"best-selling","template_suffix":"","disjunctive":false,"rules":[{"column":"tag","relation":"equals","condition":"30% off"},{"column":"tag","relation":"equals","condition":"2025spr"}],"published_scope":"web"},{"id":299769954443,"handle":"2025-special-spring-sale-accessories","title":"2025 Special Spring Sale Accessories","updated_at":"2026-05-23T19:01:34+08:00","body_html":"","published_at":"2025-04-08T19:30:19+08:00","sort_order":"best-selling","template_suffix":"","disjunctive":false,"rules":[{"column":"tag","relation":"equals","condition":"2025spr"},{"column":"tag","relation":"equals","condition":"Accessories"}],"published_scope":"web"},{"id":303633137803,"handle":"2025-summer-sale-accessories","title":"2025 Summer Sale Accessories","updated_at":"2026-05-18T19:01:22+08:00","body_html":"","published_at":"2025-07-24T16:27:39+08:00","sort_order":"best-selling","template_suffix":"","disjunctive":false,"rules":[{"column":"tag","relation":"equals","condition":"2025 Summer"},{"column":"tag","relation":"equals","condition":"Accessories"}],"published_scope":"web"},{"id":308667252875,"handle":"bfcm2025-30-off","title":"Christmas \u0026 New Year Sale 30%off","updated_at":"2026-05-16T19:01:25+08:00","body_html":"","published_at":"2025-11-25T17:22:30+08:00","sort_order":"best-selling","template_suffix":"","disjunctive":false,"rules":[{"column":"tag","relation":"equals","condition":"30% off"},{"column":"tag","relation":"equals","condition":"BFCM2025"}],"published_scope":"web"},{"id":2188869645,"handle":"new-arrival","updated_at":"2026-05-23T19:01:34+08:00","published_at":"2017-11-26T17:12:33+08:00","sort_order":"manual","template_suffix":"","published_scope":"web","title":"New arrival","body_html":"","image":{"created_at":"2022-03-15T11:21:01+08:00","alt":null,"width":2000,"height":2000,"src":"\/\/kbdfans.com\/cdn\/shop\/collections\/new_arrival.jpg?v=1647314462"}},{"id":282050461835,"handle":"on-sale-items","title":"On-sale items","updated_at":"2026-05-24T10:26:43+08:00","body_html":"Can be applied the Shopify discount code","published_at":"2023-03-02T12:57:12+08:00","sort_order":"best-selling","template_suffix":"","disjunctive":false,"rules":[{"column":"tag","relation":"equals","condition":"on-sale"}],"published_scope":"web"},{"id":37908906042,"handle":"all","title":"Products","updated_at":"2026-05-24T10:26:43+08:00","body_html":null,"published_at":"2018-05-04T14:25:20+08:00","sort_order":"created-desc","template_suffix":null,"disjunctive":false,"rules":[{"column":"type","relation":"not_equals","condition":"mw_hidden_cart_fee"},{"column":"type","relation":"not_equals","condition":"Product Fee"},{"column":"type","relation":"not_equals","condition":"mw_product_option"},{"column":"type","relation":"not_equals","condition":"mw_switcher_product"},{"column":"type","relation":"not_contains","condition":"zakeke-design"}],"published_scope":"web"},{"id":308668104843,"handle":"bfcm2025-accessories","title":"Spring Sale Accessories","updated_at":"2026-05-23T19:01:34+08:00","body_html":"","published_at":"2025-11-25T17:46:19+08:00","sort_order":"best-selling","template_suffix":"","disjunctive":false,"rules":[{"column":"tag","relation":"equals","condition":"BFCM2025"},{"column":"tag","relation":"equals","condition":"Accessories"}],"published_scope":"web"},{"id":426140813,"handle":"switches","updated_at":"2026-05-23T19:01:34+08:00","published_at":"2017-04-15T12:11:49+08:00","sort_order":"created-desc","template_suffix":"","published_scope":"web","title":"Switches","body_html":"\u003cdiv class=\"shogun-root\" data-shogun-id=\"635a42dc7cd40100cb0c14b2\" data-shogun-site-id=\"be5a2c2a-7dab-4b1d-af92-e98b67c8220b\" data-shogun-page-id=\"635a42dc7cd40100cb0c14b2\" data-shogun-page-version-id=\"635a42dc7cd40100cb0c14b1\" data-shogun-platform-type=\"shopify\" data-shogun-variant-id=\"635a42dc7cd40100cb0c14b3\" data-region=\"main\"\u003e\n  \n\n\u003cdiv id=\"s-a759190e-c0c1-4b10-b75c-e84726ad8c56\" class=\"shg-c  \"\u003e\n  \u003cdiv class=\"shogun-root\" data-shogun-id=\"635a3e760589850128a2e9eb\" data-shogun-site-id=\"be5a2c2a-7dab-4b1d-af92-e98b67c8220b\" data-shogun-page-id=\"635a3e760589850128a2e9eb\" data-shogun-page-version-id=\"635a3e760589850128a2e9ea\" data-shogun-platform-type=\"shopify\" data-shogun-variant-id=\"635a3e760589850128a2e9ec\" data-region=\"main\"\u003e\u003cdiv id=\"s-6ba371d1-7909-4a7f-8ae4-5946c9d22a6a\" class=\"shg-c  \"\u003e\u003c\/div\u003e\u003c\/div\u003e\n\n\u003c\/div\u003e\n\n\n  \n\u003c\/div\u003e\n","image":{"created_at":"2022-03-15T11:17:51+08:00","alt":null,"width":2000,"height":2000,"src":"\/\/kbdfans.com\/cdn\/shop\/collections\/switches.jpg?v=1647314272"}},{"id":285168763019,"handle":"test","title":"test","updated_at":"2026-05-18T19:01:22+08:00","body_html":"","published_at":"2023-12-01T10:21:57+08:00","sort_order":"best-selling","template_suffix":"","disjunctive":true,"rules":[{"column":"tag","relation":"equals","condition":"30% off"},{"column":"tag","relation":"equals","condition":"40% off"},{"column":"tag","relation":"equals","condition":"50% off"}],"published_scope":"web"}];
    </script>
  

  <div id="ImageUploaderContainer"></div>


  
		<script type="text/javascript" async="" src="https://cdn.littlebesidesme.com/PIU/setting.js"></script>
	
  
	
		<link rel="stylesheet" href="https://cdn.littlebesidesme.com/PIU/main.css?v=b6fafd224">
	
	
		<script type="text/javascript" async="" src="https://cdn.littlebesidesme.com/PIU/main.js?v=b6fafd224"></script>
	
	
		<script type="text/javascript" async="" src="https://cdn.littlebesidesme.com/PIU/commons.js?v=b6fafd224"></script>
	



</div>
            <div id="shopify-block-AY3FySmtNK1ZqazBoN__a7b5731e-9591-4625-beca-a30e4123ff09" class="shopify-block shopify-app-block">



















</div>
            <form method="post" action="/cart/add" id="product-form-template--16956097593483__main7095715922059" accept-charset="UTF-8" class="row ajax-product-form" enctype="multipart/form-data"><input type="hidden" name="form_type" value="product"><input type="hidden" name="utf8" value="✓"><select name="id" class="no-js" data-product-select="" aria-label="Options"><option value="41284919197835" selected="" data-stock="in">Default Title</option></select>

                    <div class="large-row with-payment-buttons"><div class="qty-wrapper">
  
<div class="cc-select cc-select--label-inside no-js-hidden cc-initialized" id="qty-proxy"><label id="qty-proxy-label" class="label no-js-hidden">Quantity</label><button class="cc-select__btn" type="button" aria-haspopup="listbox" aria-labelledby="qty-proxy-label" style="width: 464px;">1<svg class="cc-select__icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="6 9 12 15 18 9"></polyline></svg>
  </button>
  <ul class="cc-select__listbox" role="listbox" tabindex="-1" aria-hidden="true" aria-activedescendant="qty-proxy-opt0"><li class="cc-select__option js-option" id="qty-proxy-opt-0" role="option" data-value="1" aria-selected="true">
        <span>1</span>
      </li><li class="cc-select__option js-option" id="qty-proxy-opt-1" role="option" data-value="2">
        <span>2</span>
      </li><li class="cc-select__option js-option" id="qty-proxy-opt-2" role="option" data-value="3">
        <span>3</span>
      </li><li class="cc-select__option js-option" id="qty-proxy-opt-3" role="option" data-value="4">
        <span>4</span>
      </li><li class="cc-select__option js-option" id="qty-proxy-opt-4" role="option" data-value="5">
        <span>5</span>
      </li><li class="cc-select__option js-option" id="qty-proxy-opt-5" role="option" data-value="6">
        <span>6</span>
      </li><li class="cc-select__option js-option" id="qty-proxy-opt-6" role="option" data-value="7">
        <span>7</span>
      </li><li class="cc-select__option js-option" id="qty-proxy-opt-7" role="option" data-value="8">
        <span>8</span>
      </li><li class="cc-select__option js-option" id="qty-proxy-opt-8" role="option" data-value="9">
        <span>9</span>
      </li><li class="cc-select__option js-option" id="qty-proxy-opt-9" role="option" data-value="10+">
        <span>10+</span>
      </li></ul>
</div>
  <div class="qty-actual">
    <label class="qty-actual__label" for="Quantity">Quantity</label>
    <input class="qty-actual__input" type="number" id="Quantity" name="quantity" value="1">
  </div>
</div>

<div class="payment-buttons"><button class="btn btn--secondary" type="submit" name="add" data-add-to-cart="">
                            <span data-add-to-cart-text="">Add to Cart
</span>
                        </button>

                        
                          <div data-shopify="payment-button" class="shopify-payment-button"> <shopify-accelerated-checkout recommended="{&quot;supports_subs&quot;:false,&quot;supports_def_opts&quot;:false,&quot;name&quot;:&quot;paypal&quot;,&quot;wallet_params&quot;:{&quot;shopId&quot;:14733902,&quot;countryCode&quot;:&quot;CN&quot;,&quot;merchantName&quot;:&quot;KBDfans® Mechanical Keyboards Store&quot;,&quot;phoneRequired&quot;:true,&quot;companyRequired&quot;:false,&quot;shippingType&quot;:&quot;shipping&quot;,&quot;shopifyPaymentsEnabled&quot;:false,&quot;hasManagedSellingPlanState&quot;:false,&quot;requiresBillingAgreement&quot;:false,&quot;merchantId&quot;:&quot;NGK83PCMNGEVG&quot;,&quot;sdkUrl&quot;:&quot;https://www.paypal.com/sdk/js?components=buttons\u0026commit=false\u0026currency=USD\u0026locale=en_US\u0026client-id=AexZEtAxk09Ncgj6FSWFFyGKbxxAZ_LTyJ2DPdJWl1YUlecinmc5AfIaRF2qYjWlusWahlzz6SVkY5Ci\u0026merchant-id=NGK83PCMNGEVG\u0026intent=authorize&quot;}}" fallback="{&quot;supports_subs&quot;:true,&quot;supports_def_opts&quot;:true,&quot;name&quot;:&quot;buy_it_now&quot;,&quot;wallet_params&quot;:{}}" access-token="1a16cd3bb47673601af7a0f4d8acea60" buyer-country="US" buyer-locale="en" buyer-currency="USD" variant-params="[{&quot;id&quot;:41284919197835,&quot;requiresShipping&quot;:true}]" shop-id="14733902" requires-shipping="" class=""><shopify-paypal-button access-token="1a16cd3bb47673601af7a0f4d8acea60" buyer-country="US" buyer-currency="USD" wallet-params="{&quot;shopId&quot;:14733902,&quot;countryCode&quot;:&quot;CN&quot;,&quot;merchantName&quot;:&quot;KBDfans® Mechanical Keyboards Store&quot;,&quot;phoneRequired&quot;:true,&quot;companyRequired&quot;:false,&quot;shippingType&quot;:&quot;shipping&quot;,&quot;shopifyPaymentsEnabled&quot;:false,&quot;hasManagedSellingPlanState&quot;:false,&quot;requiresBillingAgreement&quot;:false,&quot;merchantId&quot;:&quot;NGK83PCMNGEVG&quot;,&quot;sdkUrl&quot;:&quot;https://www.paypal.com/sdk/js?components=buttons&amp;commit=false&amp;currency=USD&amp;locale=en_US&amp;client-id=AexZEtAxk09Ncgj6FSWFFyGKbxxAZ_LTyJ2DPdJWl1YUlecinmc5AfIaRF2qYjWlusWahlzz6SVkY5Ci&amp;merchant-id=NGK83PCMNGEVG&amp;intent=authorize&quot;}" page-type="product" slot="button" requires-shipping="" call-to-action=""><style>shopify-paypal-button[disabled]{opacity:.5;cursor:not-allowed}shopify-paypal-button div.paypal-buttons>iframe{z-index:auto!important;border-radius:0!important;box-shadow:none}</style><div slot="shadow-slot-uid_a2785743eb_mdm6mjk6mdg"><div id="zoid-paypal-buttons-uid_630167a8be_mdm6mjk6mdg" class="paypal-buttons paypal-buttons-context-iframe paypal-buttons-label-pay paypal-buttons-layout-horizontal" data-paypal-smart-button-version="5.0.552" style="height: 44px; transition: 0.2s ease-in-out;"><style nonce="">
                    #zoid-paypal-buttons-uid_630167a8be_mdm6mjk6mdg {
                        position: relative;
                        display: inline-block;
                        width: 100%;
                        min-height: 25px;
                        min-width: 150px;
                        font-size: 0;
                    }

                    #zoid-paypal-buttons-uid_630167a8be_mdm6mjk6mdg > iframe {
                        position: absolute;
                        top: 0;
                        left: 0;
                        width: 100%;
                        height: 100%;
                    }

                    #zoid-paypal-buttons-uid_630167a8be_mdm6mjk6mdg > iframe.component-frame {
                        z-index: 100;
                    }

                    #zoid-paypal-buttons-uid_630167a8be_mdm6mjk6mdg > iframe.prerender-frame {
                        transition: opacity .2s linear;
                        z-index: 200;
                    }

                    #zoid-paypal-buttons-uid_630167a8be_mdm6mjk6mdg > iframe.visible {
                        opacity: 1;
                    }

                    #zoid-paypal-buttons-uid_630167a8be_mdm6mjk6mdg > iframe.invisible {
                        opacity: 0;
                        pointer-events: none;
                    }

                    #zoid-paypal-buttons-uid_630167a8be_mdm6mjk6mdg > .smart-menu {
                        position: absolute;
                        z-index: 300;
                        top: 0;
                        left: 0;
                        width: 100%;
                    }
                </style><iframe style="background-color: transparent; border: medium;" allowtransparency="true" name="__zoid__paypal_buttons__eyJzZW5kZXIiOnsiZG9tYWluIjoiaHR0cHM6Ly9rYmRmYW5zLmNvbSJ9LCJtZXRhRGF0YSI6eyJ3aW5kb3dSZWYiOnsidHlwZSI6InBhcmVudCIsImRpc3RhbmNlIjowfX0sInJlZmVyZW5jZSI6eyJ0eXBlIjoicmF3IiwidmFsIjoie1widWlkXCI6XCJ6b2lkLXBheXBhbC1idXR0b25zLXVpZF82MzAxNjdhOGJlX21kbTZtams2bWRnXCIsXCJjb250ZXh0XCI6XCJpZnJhbWVcIixcInRhZ1wiOlwicGF5cGFsLWJ1dHRvbnNcIixcImNoaWxkRG9tYWluTWF0Y2hcIjp7XCJfX3R5cGVfX1wiOlwicmVnZXhcIixcIl9fdmFsX19cIjpcIlxcXFwucGF5cGFsXFxcXC4oY29tfGNuKSg6XFxcXGQrKT8kXCJ9LFwidmVyc2lvblwiOlwiMTBfNV8wXCIsXCJwcm9wc1wiOntcImZ1bmRpbmdTb3VyY2VcIjpcInBheXBhbFwiLFwic3R5bGVcIjp7XCJsYWJlbFwiOlwicGF5XCIsXCJsYXlvdXRcIjpcImhvcml6b250YWxcIixcImNvbG9yXCI6XCJnb2xkXCIsXCJzaGFwZVwiOlwic2hhcnBcIixcInRhZ2xpbmVcIjpmYWxzZSxcImhlaWdodFwiOjQ0LFwicGVyaW9kXCI6e1wiX190eXBlX19cIjpcInVuZGVmaW5lZFwifSxcIm1lbnVQbGFjZW1lbnRcIjpcImJlbG93XCIsXCJkaXNhYmxlTWF4V2lkdGhcIjp0cnVlLFwiZGlzYWJsZU1heEhlaWdodFwiOntcIl9fdHlwZV9fXCI6XCJ1bmRlZmluZWRcIn0sXCJib3JkZXJSYWRpdXNcIjo1LFwic2hvdWxkQXBwbHlSZWJyYW5kZWRTdHlsZXNcIjpmYWxzZSxcImlzQnV0dG9uQ29sb3JBQlRlc3RNZXJjaGFudFwiOmZhbHNlLFwiaXNQYXlOb3dPckxhdGVyTGFiZWxFbGlnaWJsZVwiOmZhbHNlLFwic2hvdWxkQXBwbHlQYXlOb3dPckxhdGVyTGFiZWxcIjpmYWxzZX0sXCJjcmVhdGVPcmRlclwiOntcIl9fdHlwZV9fXCI6XCJjcm9zc19kb21haW5fZnVuY3Rpb25cIixcIl9fdmFsX19cIjp7XCJpZFwiOlwidWlkXzdjODg2YmYxYmVfbWRtNm1qazZtZGdcIixcIm5hbWVcIjpcIm9cIn19LFwiY3JlYXRlQmlsbGluZ0FncmVlbWVudFwiOntcIl9fdHlwZV9fXCI6XCJ1bmRlZmluZWRcIn0sXCJvbkFwcHJvdmVcIjp7XCJfX3R5cGVfX1wiOlwiY3Jvc3NfZG9tYWluX2Z1bmN0aW9uXCIsXCJfX3ZhbF9fXCI6e1wiaWRcIjpcInVpZF9hMDQ1YzVhNzg0X21kbTZtams2bWRnXCIsXCJuYW1lXCI6XCJvbkFwcHJvdmVcIn19LFwib25DYW5jZWxcIjp7XCJfX3R5cGVfX1wiOlwiY3Jvc3NfZG9tYWluX2Z1bmN0aW9uXCIsXCJfX3ZhbF9fXCI6e1wiaWRcIjpcInVpZF81YzBkNmM1YTA4X21kbTZtams2bWRnXCIsXCJuYW1lXCI6XCJvbkNhbmNlbFwifX0sXCJvbkNsaWNrXCI6e1wiX190eXBlX19cIjpcImNyb3NzX2RvbWFpbl9mdW5jdGlvblwiLFwiX192YWxfX1wiOntcImlkXCI6XCJ1aWRfNWVkNzlkZjA2M19tZG02bWprNm1kZ1wiLFwibmFtZVwiOlwiYm91bmQgb25DbGlja1wifX0sXCJjc3BOb25jZVwiOntcIl9fdHlwZV9fXCI6XCJ1bmRlZmluZWRcIn0sXCJhcHBTd2l0Y2hXaGVuQXZhaWxhYmxlXCI6e1wiX190eXBlX19cIjpcInVuZGVmaW5lZFwifSxcInByZWZlcmVuY2VzXCI6e1wiX190eXBlX19cIjpcInVuZGVmaW5lZFwifSxcInNob3dQYXlQYWxBcHBTd2l0Y2hPdmVybGF5XCI6e1wiX190eXBlX19cIjpcImNyb3NzX2RvbWFpbl9mdW5jdGlvblwiLFwiX192YWxfX1wiOntcImlkXCI6XCJ1aWRfOTg2NmZlMjg4Nl9tZG02bWprNm1kZ1wiLFwibmFtZVwiOlwic2hvd1BheVBhbEFwcFN3aXRjaE92ZXJsYXlcIn19LFwiaGlkZVBheVBhbEFwcFN3aXRjaE92ZXJsYXlcIjp7XCJfX3R5cGVfX1wiOlwiY3Jvc3NfZG9tYWluX2Z1bmN0aW9uXCIsXCJfX3ZhbF9fXCI6e1wiaWRcIjpcInVpZF9jZDMwNjVmZTk3X21kbTZtams2bWRnXCIsXCJuYW1lXCI6XCJoaWRlUGF5UGFsQXBwU3dpdGNoT3ZlcmxheVwifX0sXCJyZWRpcmVjdFwiOntcIl9fdHlwZV9fXCI6XCJjcm9zc19kb21haW5fZnVuY3Rpb25cIixcIl9fdmFsX19cIjp7XCJpZFwiOlwidWlkX2Q5NDM3MDMzMDZfbWRtNm1qazZtZGdcIixcIm5hbWVcIjpcInJlZGlyZWN0XCJ9fSxcImxpc3RlbkZvckhhc2hDaGFuZ2VzXCI6e1wiX190eXBlX19cIjpcImNyb3NzX2RvbWFpbl9mdW5jdGlvblwiLFwiX192YWxfX1wiOntcImlkXCI6XCJ1aWRfMTEyN2ViMWUwNF9tZG02bWprNm1kZ1wiLFwibmFtZVwiOlwibGlzdGVuRm9ySGFzaENoYW5nZXNcIn19LFwicmVtb3ZlTGlzdGVuZXJGb3JIYXNoQ2hhbmdlc1wiOntcIl9fdHlwZV9fXCI6XCJjcm9zc19kb21haW5fZnVuY3Rpb25cIixcIl9fdmFsX19cIjp7XCJpZFwiOlwidWlkXzBjN2ZkN2NiMGFfbWRtNm1qazZtZGdcIixcIm5hbWVcIjpcInJlbW92ZUxpc3RlbmVyRm9ySGFzaENoYW5nZXNcIn19LFwibGlzdGVuRm9yVmlzaWJpbGl0eUNoYW5nZVwiOntcIl9fdHlwZV9fXCI6XCJjcm9zc19kb21haW5fZnVuY3Rpb25cIixcIl9fdmFsX19cIjp7XCJpZFwiOlwidWlkXzc0MDc4NzA4NmJfbWRtNm1qazZtZGdcIixcIm5hbWVcIjpcImxpc3RlbkZvclZpc2liaWxpdHlDaGFuZ2VcIn19LFwicmVtb3ZlTGlzdGVuZXJGb3JWaXNpYmlsaXR5Q2hhbmdlc1wiOntcIl9fdHlwZV9fXCI6XCJjcm9zc19kb21haW5fZnVuY3Rpb25cIixcIl9fdmFsX19cIjp7XCJpZFwiOlwidWlkX2VlZDgwYzZmODVfbWRtNm1qazZtZGdcIixcIm5hbWVcIjpcInJlbW92ZUxpc3RlbmVyRm9yVmlzaWJpbGl0eUNoYW5nZXNcIn19LFwiYWxsb3dCaWxsaW5nUGF5bWVudHNcIjp0cnVlLFwiYW1vdW50XCI6e1wiX190eXBlX19cIjpcInVuZGVmaW5lZFwifSxcImFwaVN0YWdlSG9zdFwiOntcIl9fdHlwZV9fXCI6XCJ1bmRlZmluZWRcIn0sXCJhcHBsZVBheVwiOntcIl9fdHlwZV9fXCI6XCJ1bmRlZmluZWRcIn0sXCJhcHBsZVBheVN1cHBvcnRcIjpmYWxzZSxcImJyYW5kZWRcIjp7XCJfX3R5cGVfX1wiOlwidW5kZWZpbmVkXCJ9LFwiYnV0dG9uTG9jYXRpb25cIjpcImtiZGZhbnMuY29tXCIsXCJidXR0b25TZXNzaW9uSURcIjpcInVpZF9jNmMyOWM3MDQxX21kbTZtams2bWRnXCIsXCJidXR0b25TaXplXCI6XCJsYXJnZVwiLFwiYnV5ZXJDb3VudHJ5XCI6e1wiX190eXBlX19cIjpcInVuZGVmaW5lZFwifSxcImNsaWVudEFjY2Vzc1Rva2VuXCI6e1wiX190eXBlX19cIjpcInVuZGVmaW5lZFwifSxcImN1c3RvbWVySWRcIjpcIlwiLFwiY2xpZW50SURcIjpcIkFleFpFdEF4azA5TmNnajZGU1dGRnlHS2J4eEFaX0xUeUoyRFBkSldsMVlVbGVjaW5tYzVBZklhUkYycVlqV2x1c1dhaGx6ejZTVmtZNUNpXCIsXCJjbGllbnRNZXRhZGF0YUlEXCI6XCJ1aWRfYzMxYmI4Njc5ZF9tZG02bWprNm1kY1wiLFwiY29tbWl0XCI6ZmFsc2UsXCJjb21wb25lbnRzXCI6W1wiYnV0dG9uc1wiXSxcImNyZWF0ZVN1YnNjcmlwdGlvblwiOntcIl9fdHlwZV9fXCI6XCJ1bmRlZmluZWRcIn0sXCJjcmVhdGVWYXVsdFNldHVwVG9rZW5cIjp7XCJfX3R5cGVfX1wiOlwidW5kZWZpbmVkXCJ9LFwiY3NwXCI6e1wibm9uY2VcIjpcIlwifSxcImN1cnJlbmN5XCI6XCJVU0RcIixcImRlYnVnXCI6ZmFsc2UsXCJkaXNhYmxlQ2FyZFwiOltdLFwiZGlzYWJsZUZ1bmRpbmdcIjpbXSxcImRpc2FibGVTZXRDb29raWVcIjp0cnVlLFwiZGlzcGxheU9ubHlcIjpbXSxcImVhZ2VyT3JkZXJDcmVhdGlvblwiOmZhbHNlLFwiZW5hYmxlRnVuZGluZ1wiOltdLFwiZW5hYmxlVGhyZWVEb21haW5TZWN1cmVcIjpmYWxzZSxcImVuYWJsZVZhdWx0XCI6e1wiX190eXBlX19cIjpcInVuZGVmaW5lZFwifSxcImVudlwiOlwicHJvZHVjdGlvblwiLFwiZXhwZXJpbWVudFwiOntcImVuYWJsZVZlbm1vXCI6ZmFsc2UsXCJ2ZW5tb1ZhdWx0V2l0aG91dFB1cmNoYXNlXCI6ZmFsc2UsXCJzcGJFYWdlck9yZGVyQ3JlYXRpb25cIjpmYWxzZSxcInZlbm1vV2ViRW5hYmxlZFwiOmZhbHNlLFwiaXNXZWJWaWV3RW5hYmxlZFwiOmZhbHNlLFwiaXNQYXlwYWxSZWJyYW5kRW5hYmxlZFwiOmZhbHNlLFwiaXNQYXlwYWxSZWJyYW5kQUJUZXN0RW5hYmxlZFwiOmZhbHNlLFwiZGVmYXVsdEJsdWVCdXR0b25Db2xvclwiOlwiZGVmYXVsdEJsdWVfZGFya0JsdWVcIixcImlzRWRnZUNhY2hlU3RhbGVFbmFibGVkXCI6ZmFsc2UsXCJpc0p1bm9DaXJjdWl0QnJlYWtlckVuYWJsZWRcIjpmYWxzZSxcImlzQ3Nud0Vycm9yVGVzdGluZ0VuYWJsZWRcIjpmYWxzZSxcInZlbm1vRW5hYmxlV2ViT25Ob25OYXRpdmVCcm93c2VyXCI6ZmFsc2UsXCJwYXlwYWxDcmVkaXRCdXR0b25DcmVhdGVWYXVsdFNldHVwVG9rZW5FeGlzdHNcIjpmYWxzZSxcImlzUGF5bGF0ZXJDb2JyYW5kZWRMYWJlbEVuYWJsZWRcIjpmYWxzZSxcImlzUGF5bGF0ZXJDb2JyYW5kZWRMYWJlbFJhbmRvbWl6YXRpb25FbmFibGVkXCI6dHJ1ZSxcImlzQmZjYWNoZUVuYWJsZWRcIjpmYWxzZX0sXCJleHBlcmltZW50YXRpb25cIjp7fSxcImZsb3dcIjpcInB1cmNoYXNlXCIsXCJmdW5kaW5nRWxpZ2liaWxpdHlcIjp7XCJwYXlwYWxcIjp7XCJlbGlnaWJsZVwiOnRydWUsXCJ2YXVsdGFibGVcIjp0cnVlfSxcInBheWxhdGVyXCI6e1wiZWxpZ2libGVcIjp0cnVlLFwidmF1bHRhYmxlXCI6ZmFsc2UsXCJwcm9kdWN0c1wiOntcInBheUluM1wiOntcImVsaWdpYmxlXCI6ZmFsc2UsXCJ2YXJpYW50XCI6bnVsbH0sXCJwYXlJbjRcIjp7XCJlbGlnaWJsZVwiOmZhbHNlLFwidmFyaWFudFwiOm51bGx9LFwicGF5bGF0ZXJcIjp7XCJlbGlnaWJsZVwiOnRydWUsXCJ2YXJpYW50XCI6bnVsbH19fSxcImNhcmRcIjp7XCJlbGlnaWJsZVwiOnRydWUsXCJicmFuZGVkXCI6dHJ1ZSxcImluc3RhbGxtZW50c1wiOmZhbHNlLFwidmVuZG9yc1wiOntcInZpc2FcIjp7XCJlbGlnaWJsZVwiOnRydWUsXCJ2YXVsdGFibGVcIjp0cnVlfSxcIm1hc3RlcmNhcmRcIjp7XCJlbGlnaWJsZVwiOnRydWUsXCJ2YXVsdGFibGVcIjp0cnVlfSxcImFtZXhcIjp7XCJlbGlnaWJsZVwiOnRydWUsXCJ2YXVsdGFibGVcIjp0cnVlfSxcImRpc2NvdmVyXCI6e1wiZWxpZ2libGVcIjp0cnVlLFwidmF1bHRhYmxlXCI6dHJ1ZX0sXCJoaXBlclwiOntcImVsaWdpYmxlXCI6ZmFsc2UsXCJ2YXVsdGFibGVcIjpmYWxzZX0sXCJlbG9cIjp7XCJlbGlnaWJsZVwiOmZhbHNlLFwidmF1bHRhYmxlXCI6dHJ1ZX0sXCJqY2JcIjp7XCJlbGlnaWJsZVwiOnRydWUsXCJ2YXVsdGFibGVcIjp0cnVlfSxcIm1hZXN0cm9cIjp7XCJlbGlnaWJsZVwiOnRydWUsXCJ2YXVsdGFibGVcIjp0cnVlfSxcImRpbmVyc1wiOntcImVsaWdpYmxlXCI6dHJ1ZSxcInZhdWx0YWJsZVwiOnRydWV9LFwiY3VwXCI6e1wiZWxpZ2libGVcIjp0cnVlLFwidmF1bHRhYmxlXCI6dHJ1ZX0sXCJjYl9uYXRpb25hbGVcIjp7XCJlbGlnaWJsZVwiOmZhbHNlLFwidmF1bHRhYmxlXCI6dHJ1ZX19LFwiZ3Vlc3RFbmFibGVkXCI6dHJ1ZX0sXCJ2ZW5tb1wiOntcImVsaWdpYmxlXCI6ZmFsc2UsXCJ2YXVsdGFibGVcIjpmYWxzZX0sXCJpdGF1XCI6e1wiZWxpZ2libGVcIjpmYWxzZX0sXCJjcmVkaXRcIjp7XCJlbGlnaWJsZVwiOmZhbHNlfSxcImFwcGxlcGF5XCI6e1wiZWxpZ2libGVcIjpmYWxzZX0sXCJzZXBhXCI6e1wiZWxpZ2libGVcIjpmYWxzZX0sXCJpZGVhbFwiOntcImVsaWdpYmxlXCI6ZmFsc2V9LFwiYmFuY29udGFjdFwiOntcImVsaWdpYmxlXCI6ZmFsc2V9LFwiZ2lyb3BheVwiOntcImVsaWdpYmxlXCI6ZmFsc2V9LFwiZXBzXCI6e1wiZWxpZ2libGVcIjpmYWxzZX0sXCJzb2ZvcnRcIjp7XCJlbGlnaWJsZVwiOmZhbHNlfSxcIm15YmFua1wiOntcImVsaWdpYmxlXCI6ZmFsc2V9LFwicDI0XCI6e1wiZWxpZ2libGVcIjpmYWxzZX0sXCJ3ZWNoYXRwYXlcIjp7XCJlbGlnaWJsZVwiOmZhbHNlfSxcInBheXVcIjp7XCJlbGlnaWJsZVwiOmZhbHNlfSxcImJsaWtcIjp7XCJlbGlnaWJsZVwiOmZhbHNlfSxcInRydXN0bHlcIjp7XCJlbGlnaWJsZVwiOmZhbHNlfSxcIm94eG9cIjp7XCJlbGlnaWJsZVwiOmZhbHNlfSxcImJvbGV0b1wiOntcImVsaWdpYmxlXCI6ZmFsc2V9LFwiYm9sZXRvYmFuY2FyaW9cIjp7XCJlbGlnaWJsZVwiOmZhbHNlfSxcIm1lcmNhZG9wYWdvXCI6e1wiZWxpZ2libGVcIjpmYWxzZX0sXCJtdWx0aWJhbmNvXCI6e1wiZWxpZ2libGVcIjpmYWxzZX0sXCJzYXRpc3BheVwiOntcImVsaWdpYmxlXCI6ZmFsc2V9LFwicGFpZHlcIjp7XCJlbGlnaWJsZVwiOmZhbHNlfX0sXCJnZXRQYWdlVXJsXCI6e1wiX190eXBlX19cIjpcImNyb3NzX2RvbWFpbl9mdW5jdGlvblwiLFwiX192YWxfX1wiOntcImlkXCI6XCJ1aWRfMTE0ODgxYjBjMF9tZG02bWprNm1kZ1wiLFwibmFtZVwiOlwiZ2V0UGFnZVVybFwifX0sXCJnZXRQb3B1cEJyaWRnZVwiOntcIl9fdHlwZV9fXCI6XCJjcm9zc19kb21haW5fZnVuY3Rpb25cIixcIl9fdmFsX19cIjp7XCJpZFwiOlwidWlkXzNjNDMwZmI0ZmVfbWRtNm1qazZtZGdcIixcIm5hbWVcIjpcImdldFBvcHVwQnJpZGdlXCJ9fSxcImdldFByZXJlbmRlckRldGFpbHNcIjp7XCJfX3R5cGVfX1wiOlwiY3Jvc3NfZG9tYWluX2Z1bmN0aW9uXCIsXCJfX3ZhbF9fXCI6e1wiaWRcIjpcInVpZF8yZmY2YWZmMTQ5X21kbTZtams2bWRnXCIsXCJuYW1lXCI6XCJnZXRQcmVyZW5kZXJEZXRhaWxzXCJ9fSxcImdldFF1ZXJpZWRFbGlnaWJsZUZ1bmRpbmdcIjp7XCJfX3R5cGVfX1wiOlwiY3Jvc3NfZG9tYWluX2Z1bmN0aW9uXCIsXCJfX3ZhbF9fXCI6e1wiaWRcIjpcInVpZF8zNTVkMDIyMWVlX21kbTZtams2bWRnXCIsXCJuYW1lXCI6XCJnZXRRdWVyaWVkRWxpZ2libGVGdW5kaW5nXCJ9fSxcImhvc3RlZEJ1dHRvbklkXCI6e1wiX190eXBlX19cIjpcInVuZGVmaW5lZFwifSxcImludGVudFwiOlwiYXV0aG9yaXplXCIsXCJqc1Nka0xpYnJhcnlcIjp7XCJfX3R5cGVfX1wiOlwidW5kZWZpbmVkXCJ9LFwibG9jYWxlXCI6e1wibGFuZ1wiOlwiZW5cIixcImNvdW50cnlcIjpcIlVTXCJ9LFwibWVyY2hhbnRJRFwiOltcIk5HSzgzUENNTkdFVkdcIl0sXCJtZXJjaGFudFJlcXVlc3RlZFBvcHVwc0Rpc2FibGVkXCI6ZmFsc2UsXCJtZXNzYWdlXCI6e1wiX190eXBlX19cIjpcInVuZGVmaW5lZFwifSxcIm5vbmNlXCI6XCJcIixcIm9uQ29tcGxldGVcIjp7XCJfX3R5cGVfX1wiOlwidW5kZWZpbmVkXCJ9LFwib25Jbml0XCI6e1wiX190eXBlX19cIjpcImNyb3NzX2RvbWFpbl9mdW5jdGlvblwiLFwiX192YWxfX1wiOntcImlkXCI6XCJ1aWRfMzRjNTc3NGRkYl9tZG02bWprNm1kZ1wiLFwibmFtZVwiOlwib25Jbml0XCJ9fSxcIm9uTWVzc2FnZUNsaWNrXCI6e1wiX190eXBlX19cIjpcImNyb3NzX2RvbWFpbl9mdW5jdGlvblwiLFwiX192YWxfX1wiOntcImlkXCI6XCJ1aWRfZTMzMDIzNGU2ZV9tZG02bWprNm1kZ1wiLFwibmFtZVwiOlwib25NZXNzYWdlQ2xpY2tcIn19LFwib25NZXNzYWdlSG92ZXJcIjp7XCJfX3R5cGVfX1wiOlwiY3Jvc3NfZG9tYWluX2Z1bmN0aW9uXCIsXCJfX3ZhbF9fXCI6e1wiaWRcIjpcInVpZF9hZGEzZTYwZTM0X21kbTZtams2bWRnXCIsXCJuYW1lXCI6XCJvbk1lc3NhZ2VIb3ZlclwifX0sXCJvbk1lc3NhZ2VSZWFkeVwiOntcIl9fdHlwZV9fXCI6XCJjcm9zc19kb21haW5fZnVuY3Rpb25cIixcIl9fdmFsX19cIjp7XCJpZFwiOlwidWlkXzFhMmNhOGNmNzBfbWRtNm1qazZtZGdcIixcIm5hbWVcIjpcIm9uTWVzc2FnZVJlYWR5XCJ9fSxcIm9uU2hpcHBpbmdBZGRyZXNzQ2hhbmdlXCI6e1wiX190eXBlX19cIjpcInVuZGVmaW5lZFwifSxcIm9uU2hpcHBpbmdDaGFuZ2VcIjp7XCJfX3R5cGVfX1wiOlwidW5kZWZpbmVkXCJ9LFwib25TaGlwcGluZ09wdGlvbnNDaGFuZ2VcIjp7XCJfX3R5cGVfX1wiOlwidW5kZWZpbmVkXCJ9LFwiaGFzU2hpcHBpbmdDYWxsYmFja1wiOmZhbHNlLFwicGFnZVR5cGVcIjp7XCJfX3R5cGVfX1wiOlwidW5kZWZpbmVkXCJ9LFwicGFydG5lckF0dHJpYnV0aW9uSURcIjp7XCJfX3R5cGVfX1wiOlwidW5kZWZpbmVkXCJ9LFwicGF5bWVudE1ldGhvZE5vbmNlXCI6e1wiX190eXBlX19cIjpcInVuZGVmaW5lZFwifSxcInBheW1lbnRNZXRob2RUb2tlblwiOntcIl9fdHlwZV9fXCI6XCJ1bmRlZmluZWRcIn0sXCJwYXltZW50UmVxdWVzdFwiOntcIl9fdHlwZV9fXCI6XCJ1bmRlZmluZWRcIn0sXCJwbGF0Zm9ybVwiOlwiZGVza3RvcFwiLFwicmVmZXJyZXJEb21haW5cIjpcImtiZGZhbnMuY29tXCIsXCJyZW1lbWJlclwiOntcIl9fdHlwZV9fXCI6XCJjcm9zc19kb21haW5fZnVuY3Rpb25cIixcIl9fdmFsX19cIjp7XCJpZFwiOlwidWlkX2Q5YjJkMzZhYWZfbWRtNm1qazZtZGdcIixcIm5hbWVcIjpcInJlbWVtYmVyXCJ9fSxcInJlbWVtYmVyZWRcIjpbXSxcInJlbmRlcmVkQnV0dG9uc1wiOltcInBheXBhbFwiXSxcInNlc3Npb25JRFwiOlwidWlkX2MzMWJiODY3OWRfbWRtNm1qazZtZGNcIixcInNka0NvcnJlbGF0aW9uSURcIjpcInByZWJ1aWxkXCIsXCJzZGtJbml0VGltaW5nc1wiOntcInNka0luaXRUaW1lU3RhbXBcIjoxNzc5NTkzMzQ3OTkwLFwic2RrU2NyaXB0RG93bmxvYWREdXJhdGlvblwiOjQxNCxcImlzU2RrQ2FjaGVkXCI6XCJub1wifSxcInNka1Rva2VuXCI6e1wiX190eXBlX19cIjpcInVuZGVmaW5lZFwifSxcInNlc3Npb25TdGF0ZVwiOntcImdldFwiOntcIl9fdHlwZV9fXCI6XCJjcm9zc19kb21haW5fZnVuY3Rpb25cIixcIl9fdmFsX19cIjp7XCJpZFwiOlwidWlkX2NhOWYwOTZiMGNfbWRtNm1qazZtZGdcIixcIm5hbWVcIjpcImdldFwifX0sXCJzZXRcIjp7XCJfX3R5cGVfX1wiOlwiY3Jvc3NfZG9tYWluX2Z1bmN0aW9uXCIsXCJfX3ZhbF9fXCI6e1wiaWRcIjpcInVpZF82MWE0OTk5NTg5X21kbTZtams2bWRnXCIsXCJuYW1lXCI6XCJzZXRcIn19fSxcInNob3BwZXJTZXNzaW9uSWRcIjpcIlwiLFwiZ2V0U2hvcHBlckluc2lnaHRzVXNlZFwiOntcIl9fdHlwZV9fXCI6XCJjcm9zc19kb21haW5fZnVuY3Rpb25cIixcIl9fdmFsX19cIjp7XCJpZFwiOlwidWlkXzIwM2ZhMDU1NTFfbWRtNm1qazZtZGdcIixcIm5hbWVcIjpcIkJyXCJ9fSxcInN0YWdlSG9zdFwiOntcIl9fdHlwZV9fXCI6XCJ1bmRlZmluZWRcIn0sXCJzdG9yYWdlSURcIjpcInVpZF9lZDA4MTQ5NTA1X21kbTZtams2bWRjXCIsXCJzdG9yYWdlU3RhdGVcIjp7XCJnZXRcIjp7XCJfX3R5cGVfX1wiOlwiY3Jvc3NfZG9tYWluX2Z1bmN0aW9uXCIsXCJfX3ZhbF9fXCI6e1wiaWRcIjpcInVpZF9lNGM5NzE3ODgzX21kbTZtams2bWRnXCIsXCJuYW1lXCI6XCJnZXRcIn19LFwic2V0XCI6e1wiX190eXBlX19cIjpcImNyb3NzX2RvbWFpbl9mdW5jdGlvblwiLFwiX192YWxfX1wiOntcImlkXCI6XCJ1aWRfOTMwOTczMDhjNV9tZG02bWprNm1kZ1wiLFwibmFtZVwiOlwic2V0XCJ9fX0sXCJidXR0b25Db2xvclwiOntcInNob3VsZEFwcGx5UmVicmFuZGVkU3R5bGVzXCI6ZmFsc2UsXCJjb2xvclwiOlwiZ29sZFwiLFwiaXNCdXR0b25Db2xvckFCVGVzdE1lcmNoYW50XCI6ZmFsc2V9LFwic3VwcG9ydGVkTmF0aXZlQnJvd3NlclwiOmZhbHNlLFwic3VwcG9ydGVkTmF0aXZlVmVubW9Ccm93c2VyXCI6ZmFsc2UsXCJzdXBwb3J0c1BvcHVwc1wiOnRydWUsXCJzdXBwb3J0c1Zlbm1vUG9wdXBzXCI6dHJ1ZSxcInRlc3RcIjp7XCJhY3Rpb25cIjpcImNoZWNrb3V0XCJ9LFwidXNlckV4cGVyaWVuY2VGbG93XCI6e1wiX190eXBlX19cIjpcInVuZGVmaW5lZFwifSxcInVzZXJJRFRva2VuXCI6e1wiX190eXBlX19cIjpcInVuZGVmaW5lZFwifSxcInNka1NvdXJjZVwiOntcIl9fdHlwZV9fXCI6XCJ1bmRlZmluZWRcIn0sXCJ2YXVsdFwiOmZhbHNlLFwid2FsbGV0XCI6e1wiX190eXBlX19cIjpcInVuZGVmaW5lZFwifSxcImhpZGVTdWJtaXRCdXR0b25Gb3JDYXJkRm9ybVwiOntcIl9fdHlwZV9fXCI6XCJ1bmRlZmluZWRcIn0sXCJ1c2VyQWdlbnRcIjpcIk1vemlsbGEvNS4wIChXaW5kb3dzIE5UIDEwLjA7IFdpbjY0OyB4NjQ7IHJ2OjE1MC4wKSBHZWNrby8yMDEwMDEwMSBGaXJlZm94LzE1MC4wXCJ9LFwiZXhwb3J0c1wiOntcImluaXRcIjp7XCJfX3R5cGVfX1wiOlwiY3Jvc3NfZG9tYWluX2Z1bmN0aW9uXCIsXCJfX3ZhbF9fXCI6e1wiaWRcIjpcInVpZF9jZjJlZTQ3OTg0X21kbTZtams2bWRnXCIsXCJuYW1lXCI6XCJpbml0XCJ9fSxcImNsb3NlXCI6e1wiX190eXBlX19cIjpcImNyb3NzX2RvbWFpbl9mdW5jdGlvblwiLFwiX192YWxfX1wiOntcImlkXCI6XCJ1aWRfM2NhOWRlZjgzOF9tZG02bWprNm1kZ1wiLFwibmFtZVwiOlwiY2xvc2U6Om1lbW9pemVkXCJ9fSxcImNoZWNrQ2xvc2VcIjp7XCJfX3R5cGVfX1wiOlwiY3Jvc3NfZG9tYWluX2Z1bmN0aW9uXCIsXCJfX3ZhbF9fXCI6e1wiaWRcIjpcInVpZF85ZGE3YzJjZWRjX21kbTZtams2bWRnXCIsXCJuYW1lXCI6XCJjaGVja0Nsb3NlXCJ9fSxcInJlc2l6ZVwiOntcIl9fdHlwZV9fXCI6XCJjcm9zc19kb21haW5fZnVuY3Rpb25cIixcIl9fdmFsX19cIjp7XCJpZFwiOlwidWlkXzY3MDQ3N2U5ZmZfbWRtNm1qazZtZGdcIixcIm5hbWVcIjpcInhuXCJ9fSxcIm9uRXJyb3JcIjp7XCJfX3R5cGVfX1wiOlwiY3Jvc3NfZG9tYWluX2Z1bmN0aW9uXCIsXCJfX3ZhbF9fXCI6e1wiaWRcIjpcInVpZF8zMGYwZDE1MmQ1X21kbTZtams2bWRnXCIsXCJuYW1lXCI6XCJEblwifX0sXCJzaG93XCI6e1wiX190eXBlX19cIjpcImNyb3NzX2RvbWFpbl9mdW5jdGlvblwiLFwiX192YWxfX1wiOntcImlkXCI6XCJ1aWRfZjhlYzQ0NmQ5Nl9tZG02bWprNm1kZ1wiLFwibmFtZVwiOlwiY25cIn19LFwiaGlkZVwiOntcIl9fdHlwZV9fXCI6XCJjcm9zc19kb21haW5fZnVuY3Rpb25cIixcIl9fdmFsX19cIjp7XCJpZFwiOlwidWlkXzNmYmQxMzYxMzFfbWRtNm1qazZtZGdcIixcIm5hbWVcIjpcImRuXCJ9fSxcImV4cG9ydFwiOntcIl9fdHlwZV9fXCI6XCJjcm9zc19kb21haW5fZnVuY3Rpb25cIixcIl9fdmFsX19cIjp7XCJpZFwiOlwidWlkX2Q4ZDM3YTUzNzRfbWRtNm1qazZtZGdcIixcIm5hbWVcIjpcIlVuXCJ9fX19In19__" title="PayPal-paypal" allowpaymentrequest="allowpaymentrequest" scrolling="no" role="presentation" id="jsx-iframe-f02582b34c" class="component-frame visible"></iframe><div id="smart-menu" class="smart-menu"></div><div id="installments-modal" class="installments-modal"></div><iframe name="__detect_close_uid_ac54dcca07_mdm6mjk6mdg__" style="display: none;"></iframe></div></div></shopify-paypal-button><more-payment-options-link buyer-country="US" access-token="1a16cd3bb47673601af7a0f4d8acea60" page-type="product" wallet-instrument-name="PayPal" slot="more-options"><a class="shopify-payment-button__more-options" id="more-payment-options-link" href="#">More payment options</a><style>#more-payment-options-link{cursor:pointer}</style></more-payment-options-link></shopify-accelerated-checkout> </div>
                        
                      </div><span style="width:100%;margin-bottom:0.75rem;margin-top:0.75rem;display:block;" class="heymerch-stockcount-container heymerch-stockcount-customcss">
  <!-- BEGIN app snippet: stock --><script src="https://cdn.shopify.com/extensions/019c6af1-cca8-7720-860c-63b21772db62/shopify-app-vue-template-46/assets/stock-show.js" defer=""></script>
<script src="https://cdn.shopify.com/extensions/019c6af1-cca8-7720-860c-63b21772db62/shopify-app-vue-template-46/assets/cookie-manager.js" defer=""></script>






<span class="heymerch-stockcount-wrapper-stock"></span>

<script>
  var heymerchStockCountVariantId="41284919197835";
  var heymerchStockCountProductId="7095715922059";
  
  var heymerchStockCountVariantList = {};
  var heymerchStockCountVariantAvailableList = {};
  var heymerchStockCountVariantPolicyList= {};
  var heymerchStockCountCollectionList=[];
  var collectionListSet = new Set();
  var allProducts = [];
  var productHandles = {};
  var quantityOfFirstNonZeroVariant = 0;
  var tracked_variant_found = false;

  
  
  
  
    
      heymerchStockCountVariantList[41284919197835] = 82;
      heymerchStockCountVariantAvailableList[41284919197835] = "shopify";
      heymerchStockCountVariantPolicyList[41284919197835] = "deny";
    
    // Expose total variants count for post-load enhancement
    var heymerchStockCountTotalVariants = 1;
    

  var heymerchStockCountProductAvailable = true;
  var heymerchStockCountTotalInventory= 82;

  
    heymerchStockCountCollectionList.push("286583423115")
  
    heymerchStockCountCollectionList.push("299770019979")
  
    heymerchStockCountCollectionList.push("299769954443")
  
    heymerchStockCountCollectionList.push("303633137803")
  
    heymerchStockCountCollectionList.push("308667252875")
  
    heymerchStockCountCollectionList.push("2188869645")
  
    heymerchStockCountCollectionList.push("282050461835")
  
    heymerchStockCountCollectionList.push("37908906042")
  
    heymerchStockCountCollectionList.push("308668104843")
  
    heymerchStockCountCollectionList.push("426140813")
  
    heymerchStockCountCollectionList.push("285168763019")
  
</script>
<!-- END app snippet -->
  <!-- BEGIN app snippet: sold -->

<script defer="">
    var initSold = function(){
      var data= window.heymerchStockCountData;

      if(!data.soldWidget.isActive){
        heymerchStockCountJquery('.heymerch-stockcount-wrapper-sold').remove()
    }else{

      heymerchStockCountJquery('.heymerch-stockcount-emoji-sold').html(data.soldWidget.soldEmoji)

        heymerchStockCountJquery('.heymerch-stockcount-text-sold').html(data.soldWidget.soldText)
        heymerchStockCountJquery('.heymerch-stockcount-text-sold').css("color",data.soldWidget.soldTextColor)
        heymerchStockCountJquery('.heymerch-stockcount-text-sold').css("font-size",""+data.soldWidget.soldTextSize+"px")

        heymerchStockCountJquery('.heymerch-stockcount-number-sold').css("color",data.soldWidget.soldNumberColor)
        heymerchStockCountJquery('.heymerch-stockcount-number-sold').css("font-size",""+data.soldWidget.soldNumberSize+"px")

        if(!data.soldWidget.soldIsUseRealData){
          const min=data.soldWidget.soldGenerateSalesDataBetweenVariable1;
          const max=data.soldWidget.soldGenerateSalesDataBetweenVariable2;

          const soldCount=getRandomInt(min,max)
          heymerchStockCountJquery('.heymerch-stockcount-number-sold').html(soldCount)
        }
    }

    }
    var collectionList2=[];
    
      collectionList2.push ( "286583423115");
  
      collectionList2.push ( "299770019979");
  
      collectionList2.push ( "299769954443");
  
      collectionList2.push ( "303633137803");
  
      collectionList2.push ( "308667252875");
  
      collectionList2.push ( "2188869645");
  
      collectionList2.push ( "282050461835");
  
      collectionList2.push ( "37908906042");
  
      collectionList2.push ( "308668104843");
  
      collectionList2.push ( "426140813");
  
      collectionList2.push ( "285168763019");
  

    var controlSolddata = function () {
      const data= window.heymerchStockCountData;

      if (data) {
          const isExclude = data.widgetSettings.selectedForExclude;
            if (data.widgetDisplay.showFor == "all") {
              initSold();
            } else if (data.widgetDisplay.showFor == "selectedProducts") {
              if (isExclude) {
                if (
                  !data.widgetData.selectedProducts.includes(heymerchStockCountProductId)
                ) {
                  initSold();
                }
              } else {
                if (
                  data.widgetData.selectedProducts.includes(heymerchStockCountProductId)
                ) {
                  initSold();
                }
              }
            } else if (data.widgetDisplay.showFor == "selectedCollections") {
              let resultCollection = false;
              if (isExclude) {
                heymerchStockCountCollectionList.forEach((collection) => {
                  if (!data.widgetData.selectedCollections.includes(collection)) {
                    resultCollection = true;
                  }
                });
              } else {
                heymerchStockCountCollectionList.forEach((collection) => {
                  if (data.widgetData.selectedCollections.includes(collection)) {
                    resultCollection = true;
                  }
                });
              }
              if (resultCollection) {
                initSold();
              } else {
                //console.log("Collection not found");
              }
            }

      } else {
        setTimeout(() => {
          controlSolddata();
        }, 500);
      }
    };

    controlSolddata();
</script>
<!-- END app snippet -->
</span>
                    </div>

<div class="store-availability-container-outer store-availability-initialized store-availability-loading" data-store-availability-container="7095715922059" data-section-url="/variants/VARIANT_ID/?section_id=store-availability" data-has-only-default-variant="true" data-single-variant-id="41284919197835" data-single-variant-product-title="Cherry MX Black Clear-Top Switches MX1A-61NW Linear Switches" data-single-variant-product-available="true" style="height: 0px;">
</div>
    <div class="backorder hidden">
      
    <p>
      <span class="backorder__variant">
        Cherry MX Black Clear-Top Switches MX1A-61NW Linear Switches
        
      </span>
      is backordered and will ship as soon as it is back in stock.
    </p>
  
    </div>                  
<input type="hidden" name="product-id" value="7095715922059"><input type="hidden" name="section-id" value="template--16956097593483__main"></form>    
            <div class="product-detail__sku sku-wrapper ">
                    SKU:
                    <span class="sku-wrapper__sku">ZH10371</span>
                  </div>
            <div class="sharing social-links">
  <span class="sharing-label">Share</span>
  <ul class="sharing-list">
    <li class="facebook">
      <a class="sharing-link" target="_blank" rel="noopener" href="//www.facebook.com/sharer.php?u=https://kbdfans.com/products/cherry-mx-black-clear-top-switches-mx1a-61nw-linear-switches">
        <span aria-hidden="true"><svg aria-hidden="true" focusable="false" role="presentation" class="icon svg-facebook" viewBox="0 0 24 24"><path d="M22.676 0H1.324C.593 0 0 .593 0 1.324v21.352C0 23.408.593 24 1.324 24h11.494v-9.294H9.689v-3.621h3.129V8.41c0-3.099 1.894-4.785 4.659-4.785 1.325 0 2.464.097 2.796.141v3.24h-1.921c-1.5 0-1.792.721-1.792 1.771v2.311h3.584l-.465 3.63H16.56V24h6.115c.733 0 1.325-.592 1.325-1.324V1.324C24 .593 23.408 0 22.676 0"></path></svg></span>
        <span class="visually-hidden">Share on Facebook</span>
      </a>
    </li>
    <li class="twitter">
      <a class="sharing-link" target="_blank" rel="noopener" href="//twitter.com/intent/tweet?text=Cherry%20MX%20Black%20Clear-Top%20Switches%20MX1A-61NW%20Linear%20Switches&amp;url=https://kbdfans.com/products/cherry-mx-black-clear-top-switches-mx1a-61nw-linear-switches">
        <span aria-hidden="true"><svg aria-hidden="true" focusable="false" role="presentation" class="icon svg-twitter svg-x" viewBox="0 0 24 24"><path fill="currentColor" d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"></path></svg></span>
        <span class="visually-hidden">Share on Twitter</span>
      </a>
    </li>
    
    <li class="pinterest">
      <a class="sharing-link" target="_blank" rel="noopener" href="//pinterest.com/pin/create/button/?url=https://kbdfans.com/products/cherry-mx-black-clear-top-switches-mx1a-61nw-linear-switches&amp;media=//kbdfans.com/cdn/shop/products/1_66b4db7d-a8ac-46b7-8686-aff540843f89_1024x1024.jpg?v=1677486850&amp;description=Cherry%20MX%20Black%20Clear-Top%20Switches%20MX1A-61NW%20Linear%20Switches">
        <span aria-hidden="true"><svg aria-hidden="true" focusable="false" role="presentation" class="icon svg-pinterest" viewBox="0 0 24 24"><path d="M12.017 0C5.396 0 .029 5.367.029 11.987c0 5.079 3.158 9.417 7.618 11.162-.105-.949-.199-2.403.041-3.439.219-.937 1.406-5.957 1.406-5.957s-.359-.72-.359-1.781c0-1.663.967-2.911 2.168-2.911 1.024 0 1.518.769 1.518 1.688 0 1.029-.653 2.567-.992 3.992-.285 1.193.6 2.165 1.775 2.165 2.128 0 3.768-2.245 3.768-5.487 0-2.861-2.063-4.869-5.008-4.869-3.41 0-5.409 2.562-5.409 5.199 0 1.033.394 2.143.889 2.741.099.12.112.225.085.345-.09.375-.293 1.199-.334 1.363-.053.225-.172.271-.401.165-1.495-.69-2.433-2.878-2.433-4.646 0-3.776 2.748-7.252 7.92-7.252 4.158 0 7.392 2.967 7.392 6.923 0 4.135-2.607 7.462-6.233 7.462-1.214 0-2.354-.629-2.758-1.379l-.749 2.848c-.269 1.045-1.004 2.352-1.498 3.146 1.123.345 2.306.535 3.55.535 6.607 0 11.985-5.365 11.985-11.987C23.97 5.39 18.592.026 11.985.026L12.017 0z"></path></svg></span>
        <span class="visually-hidden">Pin it</span>
      </a>
    </li>
    
  </ul>
</div> 
          </div>
        ].
- Inside the loop, call `save_item_data` from `core_engine.py` for every single item found.


# Instructions for Codex
Generate the Python script. Ensure the loop handles missing prices gracefully (e.g., if an item says "Sold Out" instead of a price). Add a brief delay (e.g., `time.sleep(2)`) so we don't overwhelm their servers.