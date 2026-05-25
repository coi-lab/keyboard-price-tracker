# Project Context
Build a site-specific paginated scraper for CannonKeys that feeds into our core engine. 

# Tech Stack
Python, Requests, BeautifulSoup (bs4), JSON

# Core Requirements
- Target URL: [https://cannonkeys.com/collections/switches]
- Import exact shared utilities from `core.core_engine`: `USER_AGENT`, `clean_text`, `fetch_html`, `initialize_database`, `save_item_data`.
- **Parsing Strategy (JSON-First):** CannonKeys is a Shopify store. The script MUST first attempt to extract product data by finding hidden JSON objects inside `<script>` tags. Only if the JSON parse fails should it fall back to standard BeautifulSoup HTML DOM parsing.
- **Brand Inference:** Create a robust `infer_brand(name)` function using regex. CannonKeys carries many brands, so include patterns for: Gateron, Cherry, Kailh, JWK, Tecsee, KTT, SP-Star, Aflion, Durock, and TTC. Default to "CannonKeys" if no match is found.
- Implement a `while` loop for pagination, fetching `?page=X` sequentially.
- Include a `time.sleep(2)` delay between page requests.
- Call `save_item_data` for every valid item, passing `vendor_name="CannonKeys"`. Ensure the loop handles missing/sold-out prices without crashing.

# HTML & JSON Context for AI
[Right-click the page, click 'View Page Source', and Ctrl+F for "application/json" or "product". Paste a chunk of the raw JSON script data here so Codex can see the exact dictionary structure]
In the brackets above i dont know how to do that since there are many application/jsons so you will have to look for yourself. 
            <div class="title-row">
              <h1 class="product-title">Gateron Magnetic Moonlight Linear Switch</h1>
            </div>
            <div class="price-container">
              <div class="product-info__price product-price product-price--large">
                  
<div class="price">
  <div class="price__default">
    <span class="price__current">$21.60
</span>
    <span class="price__was"></span></div>
    <div class="unit-price" hidden="">
      <span class="visually-hidden">Unit price</span>
      <span class="unit-price__price"></span>
      <span class="unit-price__separator"> / </span>
      <span class="unit-price__unit">
      </span>
    </div>
  

  
    <div class="price__no-variant" hidden="">
      <strong class="price__current">Unavailable</strong>
    </div>
  
</div>

</div>

              <div class="price-descriptors"><form method="post" action="/cart/add" id="product_form_7834947092591" accept-charset="UTF-8" class="js-instalments-form" enctype="multipart/form-data"><input type="hidden" name="form_type" value="product"><input type="hidden" name="utf8" value="✓"><input type="hidden" name="id" value="43141733908591">
                  
<input type="hidden" name="product-id" value="7834947092591"><input type="hidden" name="section-id" value="template--16426236608623__main"></form>
              </div></div>
            <div class="not-in-quickbuy">
              <div id="shopify-block-Aei9tNjF0dzZMeG8yd__0384bd02-6d2e-4c29-9d01-5facc85a2c2e" class="shopify-block shopify-app-block">
<div class="jdgm-widget jdgm-preview-badge jdgm-preview-badge--with-link jdgm--done-setup" data-id="7834947092591" data-template="manual-installation" style="display: none;" data-widget-name="preview_badge" data-impressions-tracked="true">
  <div style="display:none" class="jdgm-prev-badge" data-average-rating="0.00" data-number-of-reviews="0" data-number-of-questions="0"> <span class="jdgm-prev-badge__stars" data-score="0.00" tabindex="0" aria-label="0.00 stars" role="button"> <span class="jdgm-star jdgm--off"></span><span class="jdgm-star jdgm--off"></span><span class="jdgm-star jdgm--off"></span><span class="jdgm-star jdgm--off"></span><span class="jdgm-star jdgm--off"></span> </span> <span class="jdgm-prev-badge__text">No reviews</span> </div>
</div>
</div>
            </div>
            <hr class="not-in-quickbuy">
            <div class="input-row">
<script src="//cannonkeys.com/cdn/shop/t/44/assets/variant-picker.js?v=175145544376663429761720017135" defer=""></script><variant-picker class="no-js-hidden" data-url="/products/gateron-magnetic-moonlight-linear-switch" data-update-url="true" data-show-availability="true" data-availability-mode="down" loaded=""><fieldset class="option-selector" data-selector-type="listed" data-option="Size"><legend class="label">Size</legend><div class="option-selector__btns flex flex-wrap"><input type="radio" class="opt-btn visually-hidden focus-label js-option" name="product-form-template--16426236608623__main-7834947092591-size-option" id="product-form-template--16426236608623__main-7834947092591-size-opt-0" value="36" required="" checked=""><label class="opt-label opt-label--btn btn relative text-center" for="product-form-template--16426236608623__main-7834947092591-size-opt-0">
                    <span class="js-value">36</span>
                  </label></div>
          </fieldset><script type="application/json">
        {"variants":[{"id":43141733908591,"title":"36","option1":"36","option2":null,"option3":null,"sku":"GAT-MNLT-MAG-36","requires_shipping":true,"taxable":true,"featured_image":{"id":38187074060399,"product_id":7834947092591,"position":1,"created_at":"2025-07-23T12:57:17-04:00","updated_at":"2025-07-23T12:57:31-04:00","alt":null,"width":900,"height":900,"src":"\/\/cannonkeys.com\/cdn\/shop\/files\/GateronMagneticMoonlight.jpg?v=1753289851","variant_ids":[43141733908591]},"available":true,"name":"Gateron Magnetic Moonlight Linear Switch - 36","public_title":"36","options":["36"],"price":2160,"weight":113,"compare_at_price":null,"inventory_management":"shopify","barcode":"","featured_media":{"alt":null,"id":30187032838255,"position":1,"preview_image":{"aspect_ratio":1.0,"height":900,"width":900,"src":"\/\/cannonkeys.com\/cdn\/shop\/files\/GateronMagneticMoonlight.jpg?v=1753289851"}},"requires_selling_plan":false,"selling_plan_allocations":[],"quantity_rule":{"min":1,"max":null,"increment":1}}],"formatted": {"43141733908591":{"price":"$21.60"
}}}
      </script>
    </variant-picker>

    <noscript>
      <div class="product-info__select">
        <label class="label" for="variants-7834947092591-template--16426236608623__main">Product variants</label>
        <div class="select relative">
          <select class="select w-full" id="variants-7834947092591-template--16426236608623__main" name="id" form="product-form-template--16426236608623__main-7834947092591"><option value="43141733908591"
                      
                      >36
                - $21.60
              </option></select>
        </div>
      </div>
    </noscript>
            </div>
            <buy-buttons class="buy-buttons-row block">
              <form method="post" action="/cart/add" id="product-form-template--16426236608623__main-7834947092591" accept-charset="UTF-8" class="form js-product-form" enctype="multipart/form-data" data-product-id="7834947092591"><input type="hidden" name="form_type" value="product"><input type="hidden" name="utf8" value="✓">
                <input type="hidden" name="id" value="43141733908591" required="">
                        
<div class="quantity-submit-row input-row has-spb">
                    
                      <label class="label" for="quantity">Quantity</label>
                      <quantity-wrapper class="quantity-wrapper">
                        <a href="#" data-quantity="down" aria-label="Decrease quantity"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" class="icon feather feather-minus" aria-hidden="true" focusable="false" role="presentation"><path d="M5 12h14"></path></svg></a>
                        <input aria-label="Quantity" id="quantity" type="number" name="quantity" value="1">
                        <a href="#" data-quantity="up" aria-label="Increase quantity"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" class="icon feather feather-plus" aria-hidden="true" focusable="false" role="presentation"><path d="M12 5v14M5 12h14"></path></svg></a>
                      </quantity-wrapper>
                    

                    <div class="quantity-submit-row__submit input-row">
                      <div class="js-form-error lightly-spaced-row" role="alert" hidden=""></div><button class="btn btn--large add-to-cart" type="submit" name="add" data-add-to-cart-text="Add to cart">Add to cart</button>
                    </div>
                    
                      
                        <div data-shopify="payment-button" class="shopify-payment-button"> <shopify-accelerated-checkout recommended="{&quot;supports_subs&quot;:true,&quot;supports_def_opts&quot;:false,&quot;name&quot;:&quot;shop_pay&quot;,&quot;wallet_params&quot;:{&quot;shopId&quot;:23873421376,&quot;merchantName&quot;:&quot;CannonKeys&quot;,&quot;personalized&quot;:true}}" fallback="{&quot;supports_subs&quot;:true,&quot;supports_def_opts&quot;:true,&quot;name&quot;:&quot;buy_it_now&quot;,&quot;wallet_params&quot;:{}}" access-token="bff8360034c1aa94b4f13ff593064d82" buyer-country="US" buyer-locale="en" buyer-currency="USD" variant-params="[{&quot;id&quot;:43141733908591,&quot;requiresShipping&quot;:true}]" shop-id="23873421376" requires-shipping=""><shop-pay-wallet-button access-token="bff8360034c1aa94b4f13ff593064d82" buyer-country="US" buyer-currency="USD" wallet-params="{&quot;shopId&quot;:23873421376,&quot;merchantName&quot;:&quot;CannonKeys&quot;,&quot;personalized&quot;:true}" page-type="product" slot="button" requires-shipping="" call-to-action="" personalized="true">&nbsp;</shop-pay-wallet-button><more-payment-options-link buyer-country="US" access-token="bff8360034c1aa94b4f13ff593064d82" page-type="product" wallet-instrument-name="ShopPay" slot="more-options"><a class="shopify-payment-button__more-options" id="more-payment-options-link" href="#">More payment options</a><style>#more-payment-options-link{cursor:pointer}</style></more-payment-options-link></shopify-accelerated-checkout> </div>
                      
                    

                    
                  </div>

                
              <input type="hidden" name="product-id" value="7834947092591"><input type="hidden" name="section-id" value="template--16426236608623__main"></form>
<script src="//cannonkeys.com/cdn/shop/t/44/assets/pickup-availability.js?v=110729656532710618711720017134" defer="defer"></script><pickup-availability class="no-js-hidden" available="" data-root-url="/" data-variant-id="43141733908591"><div class="pickup-status flex input-row"><div class="pickup-icon text-success-text">
        <svg class="icon" width="20" height="20" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true" focusable="false" role="presentation"><path d="m16.558 4.8.884.884-9.959 9.958-4.925-4.925.884-.884 4.041 4.041z"></path></svg>
      </div>
      <div>
        <p class="mb-0">Pickup available at <strong>RI Warehouse</strong></p>
        <p class="mb-0 text-sm">Usually ready in 2-4 days</p>
        <button class="link mt-2 text-sm js-show-pickup-info" aria-haspopup="dialog">View store information
</button>
      </div></div></pickup-availability>

</buy-buttons>

          
      

      <div class="lightish-spaced-row-above only-in-quickbuy">
        <a class="more" href="/products/gateron-magnetic-moonlight-linear-switch">
          <span class="beside-svg underline">View details</span>
          <span class="icon--small icon-natcol has-ltr-icon"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="icon feather feather-chevron-right" aria-hidden="true" focusable="false" role="presentation"><path d="m9 18 6-6-6-6"></path></svg></span>
        </a>
      </div>
    

<a class="pagination__next pagination__link text-current underline underline--on-hover" href="/collections/switches?page=2">Next »</a>

# Instructions for Codex
Generate the complete `cannonkeys_scraper.py` script. Ensure it perfectly mimics the dual-parsing (JSON -> HTML fallback) architectural style of our existing Kinetic Labs scraper.