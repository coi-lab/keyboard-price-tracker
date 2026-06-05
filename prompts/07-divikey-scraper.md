# Project Context
Build a site-specific paginated scraper for Divinikey that feeds into our core engine. 

# Tech Stack
Python, Requests, BeautifulSoup (bs4), JSON

# Core Requirements
- Target URL: [https://divinikey.com/collections/switches]
- Import exact shared utilities from `core.core_engine`: `USER_AGENT`, `clean_text`, `fetch_html`, `initialize_database`, `save_item_data`.
- **Parsing Strategy (JSON-First):** Divinikey is a Shopify store. The script MUST first attempt to extract product data by finding hidden JSON objects inside `<script>` tags (look for `application/json` or `window.Shopify`). Only if the JSON parse fails should it fall back to standard BeautifulSoup HTML DOM parsing.
- **Brand Inference:** Create a robust `infer_brand(name)` function using regex. Include patterns for: Gateron, Cherry, Kailh, JWK, Tecsee, KTT, SP-Star, Aflion, Durock, TTC, Gazzew, Akko, and Invokeys. Default to "Divinikey" if no match is found.
- Implement a `while` loop for pagination, fetching `?page=X` sequentially.
- Include a `time.sleep(2)` delay between page requests so we do not overload their servers.
- Call `save_item_data` for every valid item, passing `vendor_name="Divinikey"`. Ensure the loop handles missing/sold-out prices gracefully without crashing.

# HTML & JSON Context for AI
<link rel="alternate" type="application/json+oembed" href="https://divinikey.com/collections/switches.oembed">
<script async="async" src="/checkouts/internal/preloads.js?locale=en-US"></script>
<link rel="preconnect" href="https://shop.app" crossorigin="anonymous">
<script async="async" src="https://shop.app/checkouts/internal/preloads.js?locale=en-US&shop_id=27536490561" crossorigin="anonymous"></script>
<script id="apple-pay-shop-capabilities" type="application/json">{"shopId":27536490561,"countryCode":"US","currencyCode":"USD","merchantCapabilities":["supports3DS"],"merchantId":"gid:\/\/shopify\/Shop\/27536490561","merchantName":"Divinikey","requiredBillingContactFields":["postalAddress","email","phone"],"requiredShippingContactFields":["postalAddress","email","phone"],"shippingType":"shipping","supportedNetworks":["visa","masterCard","amex","discover","elo","jcb"],"total":{"type":"pending","label":"Divinikey","amount":"1.00"},"shopifyPaymentsEnabled":true,"supportsSubscriptions":true}</script>
<script id="shopify-features" type="application/json">{"accessToken":"a3decea06da36a08e756e688ec25bc4c","betas":["rich-media-storefront-analytics"],"domain":"divinikey.com","predictiveSearch":true,"shopId":27536490561,"locale":"en"}</script>
<script>var Shopify = Shopify || {};

<div class="product-info__sticky" style="top: -60px;"><a class="product-options--anchor" id="product-info" rel="nofollow"></a><div class="product-info__block product-info__block--sm product-info__title" data-dynamic-variant-content="template--19489031323713__main-title">
              <h1 class="product-title h5">HMX Macchiato V2 Linear Switches

                  

              </h1>
            </div><!-- Stamped - Begin Star Rating Badge -->
            <span class="stamped-product-reviews-badge stamped-main-badge" data-id="7913974038593" data-product-sku="hmx-macchiato-v2-linear-switches" data-product-title="HMX Macchiato V2 Linear Switches" data-product-type="Switches" style="display: block;"><span class="stamped-badge" data-rating="0.0" data-lang="" aria-label="Rated 0.0 out of 5 stars 0 reviews"><span class="stamped-starrating stamped-badge-starrating" aria-hidden="true"><i class="stamped-fa stamped-fa-star-o" style="color:#4a4a4a !important;" aria-hidden="true"></i><i class="stamped-fa stamped-fa-star-o" style="color:#4a4a4a !important;" aria-hidden="true"></i><i class="stamped-fa stamped-fa-star-o" style="color:#4a4a4a !important;" aria-hidden="true"></i><i class="stamped-fa stamped-fa-star-o" style="color:#4a4a4a !important;" aria-hidden="true"></i><i class="stamped-fa stamped-fa-star-o" style="color:#4a4a4a !important;" aria-hidden="true"></i></span><span class="stamped-badge-caption" data-reviews="0" data-rating="0.0" data-label="reviews" data-version="2"></span></span></span>
            <!-- Stamped - End Star Rating Badge --><div class="product-info__block product-info__block--sm product-price"><div class="product-info__price" data-dynamic-variant-content="template--19489031323713__main-price-price">
                  <div class="price">
  <div class="price__default">
    <span class="price__current">
      <span class="visually-hidden js-label">Regular price</span>
      <span class="js-value">$5.76
</span>
    </span>
    <span class="price__was">
      <span class="visually-hidden js-label"></span>
      <span class="js-value"></span>
    </span>
  </div><div class="unit-price relative" hidden=""><span class="visually-hidden">Unit price</span><span>
</span></div>
</div>

                </div><form method="post" action="/cart/add" id="instalments-form-template--19489031323713__main" accept-charset="UTF-8" class="js-instalments-form  text-sm mt-2" enctype="multipart/form-data"><input type="hidden" name="form_type" value="product"><input type="hidden" name="utf8" value="✓"><input type="hidden" name="id" value="43990854697025" data-dynamic-variant-content="template--19489031323713__main-price-input-id">
                  <shopify-payment-terms variant-id="43990854697025" shopify-meta="{&quot;type&quot;:&quot;product&quot;,&quot;currency_code&quot;:&quot;USD&quot;,&quot;country_code&quot;:&quot;US&quot;,&quot;variants&quot;:[{&quot;id&quot;:43990854697025,&quot;price_per_term&quot;:&quot;$2.88&quot;,&quot;full_price&quot;:&quot;$5.76&quot;,&quot;eligible&quot;:false,&quot;available&quot;:true,&quot;number_of_payment_terms&quot;:2}],&quot;min_price&quot;:&quot;$35.00&quot;,&quot;max_price&quot;:&quot;$30,000.00&quot;,&quot;financing_plans&quot;:[{&quot;min_price&quot;:&quot;$35.00&quot;,&quot;max_price&quot;:&quot;$49.99&quot;,&quot;terms&quot;:[{&quot;apr&quot;:0,&quot;loan_type&quot;:&quot;split_pay&quot;,&quot;installments_count&quot;:2}]},{&quot;min_price&quot;:&quot;$50.00&quot;,&quot;max_price&quot;:&quot;$149.99&quot;,&quot;terms&quot;:[{&quot;apr&quot;:0,&quot;loan_type&quot;:&quot;split_pay&quot;,&quot;installments_count&quot;:4}]},{&quot;min_price&quot;:&quot;$150.00&quot;,&quot;max_price&quot;:&quot;$999.99&quot;,&quot;terms&quot;:[{&quot;apr&quot;:0,&quot;loan_type&quot;:&quot;split_pay&quot;,&quot;installments_count&quot;:4},{&quot;apr&quot;:15,&quot;loan_type&quot;:&quot;interest&quot;,&quot;installments_count&quot;:3},{&quot;apr&quot;:15,&quot;loan_type&quot;:&quot;interest&quot;,&quot;installments_count&quot;:6},{&quot;apr&quot;:15,&quot;loan_type&quot;:&quot;interest&quot;,&quot;installments_count&quot;:12}]},{&quot;min_price&quot;:&quot;$1,000.00&quot;,&quot;max_price&quot;:&quot;$30,000.00&quot;,&quot;terms&quot;:[{&quot;apr&quot;:15,&quot;loan_type&quot;:&quot;interest&quot;,&quot;installments_count&quot;:3},{&quot;apr&quot;:15,&quot;loan_type&quot;:&quot;interest&quot;,&quot;installments_count&quot;:6},{&quot;apr&quot;:15,&quot;loan_type&quot;:&quot;interest&quot;,&quot;installments_count&quot;:12}]}],&quot;installments_buyer_prequalification_enabled&quot;:false,&quot;seller_id&quot;:631388}" data-instance-id="3ecf8a42-6e2f-4dc1-81a4-ead32f04e204"></shopify-payment-terms>
<input type="hidden" name="product-id" value="7913974038593"><input type="hidden" name="section-id" value="template--19489031323713__main"></form>
            </div><hr class="mt-8 mb-8"><div class="product-info__block">
              <div id="shopify-block-AZWVIdWRFSW1MNE9XN__king_linked_options_app_block_aFjcwm" class="shopify-block shopify-app-block">
</div>
            </div><a class="product-options--anchor" id="variants" rel="nofollow"></a><div class="product-info__block product-options" data-dynamic-variant-content="template--19489031323713__main-variant-picker"><script src="//divinikey.com/cdn/shop/t/96/assets/variant-picker.js?v=146751732743432526501771987150" defer="defer"></script><variant-picker class="variant-picker--product-available" data-option-count="1" data-section-id="template--19489031323713__main" data-url="/products/hmx-macchiato-v2-linear-switches" data-update-url="true" data-availability="true" data-select-first-variant="true" loaded=""><fieldset class="option-selector" data-selector-type="listed" data-index="1" data-option="Size"><legend class="label">Size</legend><div class="option-selector__btns flex flex-wrap"><input type="radio" class="opt-btn visually-hidden focus-label js-option" name="product-form-template--19489031323713__main-1-option" id="product-form-template--19489031323713__main-1-opt-0" value="18 Set" data-value-id="4165572264001" data-variant-id="43990854697025" required="" checked="">

            <label for="product-form-template--19489031323713__main-1-opt-0" class="opt-label opt-label--btn btn relative text-center"><span>18 Set</span></label></div>
      </fieldset>
    <script type="application/json">{"id":43990854697025,"title":"18 Set","option1":"18 Set","option2":null,"option3":null,"sku":"DK007145","requires_shipping":true,"taxable":true,"featured_image":null,"available":true,"name":"HMX Macchiato V2 Linear Switches - 18 Set","public_title":"18 Set","options":["18 Set"],"price":576,"weight":34,"compare_at_price":0,"inventory_management":"shopify","barcode":"DK007145","requires_selling_plan":false,"selling_plan_allocations":[],"quantity_rule":{"min":1,"max":null,"increment":1}}</script></variant-picker>


              </div><link href="//divinikey.com/cdn/shop/t/96/assets/product-inventory.css?v=60700778867257325721771448113" rel="stylesheet" type="text/css" media="all">
<script src="//divinikey.com/cdn/shop/t/96/assets/product-inventory.js?v=124389401363901564011771448113" defer="defer"></script>

<product-inventory class="product-info__block product-info__block--sm product-inventory block no-js-hidden" data-show-count="always" data-show-notice="low" data-threshold-low="8" data-threshold-very-low="8" data-text-very-low="&lt;p&gt;- Almost gone!&lt;/p&gt;" data-text-low="&lt;p&gt;- Hurry while stocks last!&lt;/p&gt;" data-text-normal="" data-text-no-stock="" data-text-no-stock-backordered="&lt;p&gt;Backordered&lt;/p&gt;" data-show-no-stock-backordered="true" data-inventory-level="" data-variant-available="true" data-inventory-quantity="305" data-inventory-policy="deny" data-scale="35" hidden="">
  
    <div class="product-inventory__text">
      <span class="product-inventory__status js-inventory-notice"></span>
      
    </div>
    
    <script type="application/json" data-dynamic-variant-content="template--19489031323713__main-6932030c-6385-4394-b3bb-93ddc878aa36">
      {"inventory_quantity":305,"available":true,"inventory_policy":"deny"}
    </script>
  
</product-inventory>

<hr class="mt-8 mb-8"><div class="product-info__block">
              <div id="shopify-block-AWkZ4NWhqMVN1ZXhXW__ade86b8b-f561-4b0a-9d24-c313a19418d2" class="shopify-block shopify-app-block"><!--
  Alert Me Restock Alerts App
  displayForm 
  alwaysShow false
  preorder false
  variants 
-->




  

  

  

  

  

  

  

















  <!-- variant 43990854697025 305 true -->
  

<!-- eligibleVariants false -->



</div>
            </div><div class="product-info__block">
              <product-form><form method="post" action="/cart/add" id="product-form-template--19489031323713__main" accept-charset="UTF-8" class="js-product-form js-product-form-main" enctype="multipart/form-data"><input type="hidden" name="form_type" value="product"><input type="hidden" name="utf8" value="✓"><div class="alert mb-8 bg-error-bg text-error-text js-form-error text-start" role="alert" hidden=""></div>

                    <input type="hidden" name="id" value="43990854697025" data-dynamic-variant-content="template--19489031323713__main-buy-buttons-input-id" required="">
                    <div class="product-info__add-to-cart flex" data-dynamic-variant-content="template--19489031323713__main-buy-buttons-add-to-cart">
<quantity-input class="inline-block">
  <label class="label visually-hidden" for="quantity-template--19489031323713__main">Qty</label>
  <div class="qty-input qty-input--combined inline-flex items-center w-full">
    <button type="button" class="qty-input__btn btn btn--minus no-js-hidden" name="minus" aria-controls="quantity-template--19489031323713__main">
      <span class="visually-hidden">Decrease quantity</span>
    </button>
    <input type="number" class="qty-input__input input" id="quantity-template--19489031323713__main" name="quantity" min="1" value="1">
    <button type="button" class="qty-input__btn btn btn--plus no-js-hidden" name="plus" aria-controls="quantity-template--19489031323713__main">
      <span class="visually-hidden">Increase quantity</span>
    </button>
  </div>
</quantity-input>

<div class="product-info__add-button"><button type="submit" data-add-to-cart-text="Add to cart" class="btn btn--primary w-full" name="add" data-preselection-disabled="true" data-preselection-text="Make a selection">Add to cart</button>
                      </div>
                    </div><input type="hidden" name="product-id" value="7913974038593"><input type="hidden" name="section-id" value="template--19489031323713__main"></form>
              </product-form></div><div class="product-info__block" data-dynamic-variant-content="template--19489031323713__main-pop_up_eAY7pX">
              <modal-opener class="no-js-hidden" data-modal="modal-pop_up_eAY7pX">
                <button type="button" class="btn btn--secondary" aria-haspopup="dialog">How many packs for my layout?</button>
              </modal-opener>
              <a href="" class="link js-hidden">How many packs for my layout?</a>
            </div><div class="product-info__block" data-dynamic-product-content="template--19489031323713__main-bd98920a-865e-4534-b867-99822dd13d64"><link href="//divinikey.com/cdn/shop/t/96/assets/product.css?v=28665864510390351841771450804" rel="stylesheet" type="text/css" media="all">
<link rel="stylesheet" href="//divinikey.com/cdn/shop/t/96/assets/quick-add.css?v=68655787241544613711771448119" media="all" onload="this.media='all'">
  <script src="//divinikey.com/cdn/shop/t/96/assets/quick-add.js?v=144417702492661130001771448119" defer="defer"></script>
  <script src="//divinikey.com/cdn/shop/t/96/assets/variant-picker.js?v=146751732743432526501771987150" defer="defer"></script>
  <script src="//divinikey.com/cdn/shop/t/96/assets/product-form.js?v=158227215329629734871771448112" defer="defer"></script>
  <script src="//divinikey.com/cdn/shop/t/96/assets/custom-select.js?v=87551504631488143301771448094" defer="defer"></script><product-recommendations class="block" data-url="/recommendations/products?section_id=template--19489031323713__main&amp;product_id=7913974038593&amp;limit=4&amp;intent=complementary" data-product-id="7913974038593"><carousel-slider class="carousel block">

        <div class="mb-2 flex items-center justify-between"><div class="slider-nav slide-nav--inline flex no-js-hidden">
            <button type="button" class="slider-nav__btn tap-target btn has-ltr-icon" name="prev" aria-controls="slider-template--19489031323713__main" disabled="">
              <span class="visually-hidden">Previous</span>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" focusable="false" role="presentation" class="icon"><path d="m6.797 11.625 8.03-8.03 1.06 1.06-6.97 6.97 6.97 6.97-1.06 1.06z"></path></svg>
            </button>
            <button type="button" class="slider-nav__btn slider-nav__btn--offset tap-target btn has-ltr-icon" name="next" aria-controls="slider-template--19489031323713__main">
              <span class="visually-hidden">Next</span>
              <svg width="24" height="24" viewBox="0 0 24 24" aria-hidden="true" focusable="false" role="presentation" class="icon"><path d="m9.693 4.5 7.5 7.5-7.5 7.5" stroke="currentColor" stroke-width="1.5" fill="none"></path></svg>
            </button>
          </div>
        </div>

        <div class="relative">
          <div class="slider slider--no-scrollbar is-grabbable" id="slider-template--19489031323713__main"><ul class="slider__grid grid grid-flow-col auto-cols-1 gap-x-theme small__grid" role="list"><li class="slider__item"><div class="card card--row card--related  relative flex">
  <div class="card__media">
    
<div class="media relative" style="padding-top: 100.0%;">
          <img srcset="//divinikey.com/cdn/shop/files/hmx-dirty-pink-linear-switches-2172818.webp?v=1780069749&amp;width=88, //divinikey.com/cdn/shop/files/hmx-dirty-pink-linear-switches-2172818.webp?v=1780069749&amp;width=176 2x" src="//divinikey.com/cdn/shop/files/hmx-dirty-pink-linear-switches-2172818.webp?v=1780069749&amp;width=176" class="img-fit" loading="lazy" width="176" height="176" alt="HMX Dirty Pink Linear Switches - Divinikey">
        </div>
  </div>

  <div class="card__info">
    <p class="h6 regular-text mt-2 mb-1">
      <a href="/products/hmx-dirty-pink-linear-switches?pr_prod_strat=pinned&amp;pr_rec_id=5be1877d1&amp;pr_rec_pid=7913973973057&amp;pr_ref_pid=7913974038593&amp;pr_seq=uniform" class="card-link text-current">
        HMX Dirty Pink Linear Switches
      </a>
    </p><div class="price">
  <div class="price__default">
    <span class="price__current">
      <span class="visually-hidden js-label">Regular price</span>
      <span class="js-value">$5.76
</span>
    </span>
    <span class="price__was">
      <span class="visually-hidden js-label"></span>
      <span class="js-value"></span>
    </span>
  </div><div class="unit-price relative" hidden=""><span class="visually-hidden">Unit price</span><span>
</span></div>
</div>
<button type="button" class="btn btn--secondary btn--sm js-quick-add no-js-hidden" aria-haspopup="dialog" data-product-url="/products/hmx-dirty-pink-linear-switches?pr_prod_strat=pinned&amp;pr_rec_id=5be1877d1&amp;pr_rec_pid=7913973973057&amp;pr_ref_pid=7913974038593&amp;pr_seq=uniform" data-quick-add-listener-added="true">
            
Choose options
          </button>
        </div>
</div>
</li><li class="slider__item"><div class="card card--row card--related  relative flex">
  <div class="card__media">
    
<div class="media relative" style="padding-top: 100.0%;">
          <img srcset="//divinikey.com/cdn/shop/products/tx-switch-puller-180424.webp?v=1667007251&amp;width=88, //divinikey.com/cdn/shop/products/tx-switch-puller-180424.webp?v=1667007251&amp;width=176 2x" src="//divinikey.com/cdn/shop/products/tx-switch-puller-180424.webp?v=1667007251&amp;width=176" class="img-fit" loading="lazy" width="176" height="176" alt="TX Switch Puller - Divinikey">
        </div>
  </div>

  <div class="card__info">
    <p class="h6 regular-text mt-2 mb-1">
      <a href="/products/tx-switch-puller?pr_prod_strat=pinned&amp;pr_rec_id=5be1877d1&amp;pr_rec_pid=6896744529985&amp;pr_ref_pid=7913974038593&amp;pr_seq=uniform" class="card-link text-current">
        TX Switch Puller
      </a>
    </p><div class="price">
  <div class="price__default">
    <span class="price__current">
      <span class="visually-hidden js-label">Regular price</span>
      <span class="js-value">$8.00
</span>
    </span>
    <span class="price__was">
      <span class="visually-hidden js-label"></span>
      <span class="js-value"></span>
    </span>
  </div><div class="unit-price relative" hidden=""><span class="visually-hidden">Unit price</span><span>
</span></div>
</div>
<button type="button" class="btn btn--secondary btn--sm js-quick-add no-js-hidden" aria-haspopup="dialog" data-product-url="/products/tx-switch-puller?pr_prod_strat=pinned&amp;pr_rec_id=5be1877d1&amp;pr_rec_pid=6896744529985&amp;pr_ref_pid=7913974038593&amp;pr_seq=uniform" data-quick-add-listener-added="true">
            
Choose options
          </button>
        </div>
</div>
</li><li class="slider__item"><div class="card card--row card--related  relative flex">
  <div class="card__media">
    
<div class="media relative" style="padding-top: 100.0%;">
          <img srcset="//divinikey.com/cdn/shop/files/tx-multi-tool-5-in-1-v11-5291004.webp?v=1761026749&amp;width=88, //divinikey.com/cdn/shop/files/tx-multi-tool-5-in-1-v11-5291004.webp?v=1761026749&amp;width=176 2x" src="//divinikey.com/cdn/shop/files/tx-multi-tool-5-in-1-v11-5291004.webp?v=1761026749&amp;width=176" class="img-fit" loading="lazy" width="176" height="176" alt="TX Multi - Tool 5 - in - 1 V1.1 - Divinikey">
        </div>
  </div>

  <div class="card__info">
    <p class="h6 regular-text mt-2 mb-1">
      <a href="/products/tx-multi-tool-5-in-1?pr_prod_strat=pinned&amp;pr_rec_id=5be1877d1&amp;pr_rec_pid=7568249520193&amp;pr_ref_pid=7913974038593&amp;pr_seq=uniform" class="card-link text-current">
        TX Multi-Tool 5-in-1 V1.1
      </a>
    </p><div class="price">
  <div class="price__default">
    <span class="price__current">
      <span class="visually-hidden js-label">Regular price</span>
      <span class="js-value">$22.00
</span>
    </span>
    <span class="price__was">
      <span class="visually-hidden js-label"></span>
      <span class="js-value"></span>
    </span>
  </div><div class="unit-price relative" hidden=""><span class="visually-hidden">Unit price</span><span>
</span></div>
</div>
<button type="button" class="btn btn--secondary btn--sm js-quick-add no-js-hidden" aria-haspopup="dialog" data-product-url="/products/tx-multi-tool-5-in-1?pr_prod_strat=pinned&amp;pr_rec_id=5be1877d1&amp;pr_rec_pid=7568249520193&amp;pr_ref_pid=7913974038593&amp;pr_seq=uniform" data-quick-add-listener-added="true">
            
Choose options
          </button>
        </div>
</div>
</li></ul></div>
        </div>
      </carousel-slider></product-recommendations></div><div class="product-info__block product-info__block--sm rte product-description" data-dynamic-product-content="template--19489031323713__main-5bf4b87e-31b6-4e85-bda9-6267244065e8">
                <p>HMX Macchiato V2 Switches are updated to HMX's latest improvements and utilize their L3 mold. This results in a more smooth travel with a tighter tolerance for consistency. It has a clacky sound that is surprisingly balanced to a point where it almost sounds neutral with a rich resonance.</p>
<p><strong>Sound Profile: </strong>High-pitched, Clacky, Rich, Balanced</p>
<p><b>HMX Macchiato V2 Switches Feature:</b></p>
<ul>
<li style="font-weight: bold;"><strong>18 included in each pack</strong></li>
<li>Linear</li>
<li>Manufactured by HMX</li>
<li>Designed by YG Studio</li>
<li>Top Housing: PA12</li>
<li>Bottom Housing: PA2</li>
<li>Stem: POK</li>
<li>Spring: 22mm, KOS, Single-stage</li>
<li>Pre-travel: 2.0mm</li>
<li>Total Travel: 3.8±0.2mm</li>
<li>Actuation: 50±2g</li>
<li>Bottom-out: 57±2g</li>
<li>5-Pin, PCB Mount</li>
<li>MX Structure</li>
<li>Price: $0.32 per switch</li>
</ul>
<p><strong>Includes:</strong></p>
<ul>
<li>HMX Macchiato V2 Switches</li>
</ul>
              </div></div>

<nav aria-label="Pagination">
    
      <ul class="pagination relative flex flex-wrap justify-center items-center justify-between w-full mx-auto mb-10 js-pagination" data-is-more-results="true" data-pagination-style="traditional">
        <li class="pagination__item pagination__item--arrow">
          <a class="pagination__arrow pagination__arrow--prev hover:lighten flex text-current items-center has-ltr-icon" role="link" aria-disabled="true" data-instant="">
            <span class="pagination__arrow-icon" aria-hidden="true"><svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" focusable="false" role="presentation" class="icon"><path d="m6.797 11.625 8.03-8.03 1.06 1.06-6.97 6.97 6.97 6.97-1.06 1.06z"></path></svg></span>
            <span class="pagination__prev-label mis-2">Previous</span>
          </a>
        </li>
        <li class="pagination__item text-center md:hidden font-bold">
          Page 1 / 5
        </li><li class="hidden md:block"><span class="pagination__page-current font-bold block leading-none">1</span></li><li class="hidden md:block"><a class="pagination__page-link text-current block leading-none" href="/collections/switches?page=2" data-instant="">2</a></li><li class="hidden md:block"><a class="pagination__page-link text-current block leading-none" href="/collections/switches?page=3" data-instant="">3</a></li><li class="hidden md:block"><span class="block leading-none ml-2 mr-2">…</span></li><li class="hidden md:block"><a class="pagination__page-link text-current block leading-none" href="/collections/switches?page=5" data-instant="">5</a></li><li class="pagination__item pagination__item--arrow">
          <a class="pagination__arrow pagination__arrow--next hover:lighten flex justify-end text-current items-center has-ltr-icon js-pagination-load-more" href="/collections/switches?page=2" data-instant="">
            <span class="pagination__next-label text-end">Next</span>
            <span class="pagination__arrow-icon" aria-hidden="true"><svg width="24" height="24" viewBox="0 0 24 24" aria-hidden="true" focusable="false" role="presentation" class="icon"><path d="m9.693 4.5 7.5 7.5-7.5 7.5" stroke="currentColor" stroke-width="1.5" fill="none"></path></svg></span>
          </a>
        </li>
      </ul>
    
  </nav>

# Instructions for Codex
Generate the complete `divinikey_scraper.py` script. Ensure it perfectly mimics the dual-parsing (JSON -> HTML fallback) architectural style of our existing Kinetic Labs and CannonKeys scrapers.