/* Kundeportal — dark mode. Lys modus er standard; kunden slår på mørk modus selv, og valget huskes per enhet. */
(function(){
  var KEY='arcads-tema', root=document.documentElement;
  function lagret(){try{return localStorage.getItem(KEY)}catch(e){return null}}
  function lagre(v){try{localStorage.setItem(KEY,v)}catch(e){}}
  function sett(t){root.setAttribute('data-theme',t);var b=document.querySelector('.tema-knapp');if(b){b.setAttribute('aria-label',t==='dark'?'Bytt til lys modus':'Bytt til mørk modus');b.setAttribute('aria-pressed',t==='dark')}}
  sett(lagret()==='dark'?'dark':'light');

  function brandBase(){
    var t=root.getAttribute('data-theme');root.removeAttribute('data-theme');
    var b=getComputedStyle(root).getPropertyValue('--brand').trim();
    root.setAttribute('data-theme',t);
    if(b)root.style.setProperty('--brand-base',b);
  }
  function knapp(){
    if(document.querySelector('.tema-knapp'))return;
    var b=document.createElement('button');b.type='button';b.className='tema-knapp';
    b.innerHTML='<svg class="mane" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5Z"/></svg>'+
      '<svg class="sol" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2.5v2M12 19.5v2M4.6 4.6l1.4 1.4M18 18l1.4 1.4M2.5 12h2M19.5 12h2M4.6 19.4 6 18M18 6l1.4-1.4"/></svg>';
    b.addEventListener('click',function(){var n=root.getAttribute('data-theme')==='dark'?'light':'dark';lagre(n);sett(n)});
    var wrap=document.querySelector('header .wrap');
    if(!wrap){b.classList.add('tema-flytende');document.body.appendChild(b)}
    else{
      var kontakt=wrap.querySelector('.contact');
      if(kontakt&&kontakt.parentNode===wrap){var h=document.createElement('div');h.className='tema-hoyre';wrap.insertBefore(h,kontakt);h.appendChild(kontakt);h.appendChild(b)}
      else wrap.appendChild(b);
    }
    sett(root.getAttribute('data-theme'));
  }
  function init(){brandBase();knapp()}
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
