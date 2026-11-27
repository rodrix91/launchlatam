// T-110 lazy loader for the scan box embedded in blog articles.
// scan.js (~48 KB) is fetched only when the box gets near the viewport or the reader interacts with it.
// A submit that happens before scan.js is ready is held and replayed once it loads (no native form submit).
(function(){
"use strict";
var box=document.querySelector("[data-lazy-scan]");if(!box)return;
var src=box.getAttribute("data-scan-src"),state=0,held=null; // 0 idle, 1 loading, 2 ready
function load(){if(state)return;state=1;var s=document.createElement("script");s.src=src;
 s.onload=function(){state=2;if(held){var f=held;held=null;if(f.requestSubmit)f.requestSubmit();else f.dispatchEvent(new Event("submit",{cancelable:true}))}};
 s.onerror=function(){state=0};document.head.appendChild(s)}
box.addEventListener("submit",function(e){if(state===2)return;e.preventDefault();held=e.target;load()},true);
["focusin","pointerdown","touchstart","keydown"].forEach(function(t){box.addEventListener(t,load,{passive:true})});
if("IntersectionObserver" in window){var io=new IntersectionObserver(function(es){for(var i=0;i<es.length;i++)if(es[i].isIntersecting){io.disconnect();load();return}},{rootMargin:"600px 0px"});io.observe(box)}
else load();
})();
