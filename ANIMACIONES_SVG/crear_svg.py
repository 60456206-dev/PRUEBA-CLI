from pathlib import Path
import base64
p=Path(__file__).resolve().parent
source=base64.b64encode((p/'Sin título.png').read_bytes()).decode()
svg='''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1080" height="1920" style="width:100%;height:100%" viewBox="0 0 1080 1920" role="img" aria-labelledby="title desc">
<title id="title">Cristal y ámbar — introducción animada</title>
<desc id="desc">Engranajes originales con colores intensificados sobre negro puro. Giro opuesto de ida y vuelta y vapor de hielo seco en movimiento suave y reflejos pulsantes. Cámara con acercamiento y regreso acelerados y frenados suavemente, en formato móvil 9:16. Imagen PNG integrada; no es vectorización pura.</desc>
<defs>
<image id="original" width="1024" height="1536" xlink:href="data:image/png;base64,SOURCE"/>
<path id="iceShape" d="M185 407L304 376 353 444 393 438 414 369 478 391 494 486 527 508 574 484 617 554 589 622 605 669 638 700 610 789 569 807 545 868 558 941 489 984 456 960 424 1022 356 1025 325 950 277 925 222 974 179 942 193 859 166 814 74 820 61 753 124 696 125 651 63 601 87 541 139 503 204 533 222 503 199 465Z"/><path id="metalShape" d="M669 609L747 592 774 646 803 654 825 607 879 637 883 709 916 737 946 717 978 782 947 837 960 880 987 907 973 981 931 1005 936 1066 874 1108 822 1084 790 1094 750 1133 679 1095 677 1048 634 1012 590 1021 555 959 577 909 566 864 542 844 556 784 609 777 627 743 595 704 628 665 667 681 680 651Z"/>
<filter id="edge"><feGaussianBlur stdDeviation="7"/></filter><mask id="iceClip"><use xlink:href="#iceShape" fill="white" filter="url(#edge)"/></mask>
<mask id="metalClip"><use xlink:href="#metalShape" fill="white" filter="url(#edge)"/></mask>
<mask id="backgroundOnly"><rect width="1024" height="1536" fill="white"/><g fill="black"><use xlink:href="#iceShape"/><use xlink:href="#metalShape"/></g></mask>
<filter id="color" color-interpolation-filters="sRGB">
<feColorMatrix type="saturate" values="1.38"/>
<feComponentTransfer><feFuncR type="linear" slope="1.025" intercept="-.012"/><feFuncG type="linear" slope="1.025" intercept="-.012"/><feFuncB type="linear" slope="1.025" intercept="-.012"/></feComponentTransfer>
</filter>
<filter id="soft"><feGaussianBlur stdDeviation="15"/></filter>
<filter id="vapor" x="-8%" y="-8%" width="116%" height="116%" color-interpolation-filters="sRGB">
<feTurbulence type="fractalNoise" baseFrequency=".007 .011" numOctaves="2" seed="8" result="noise"/>
<feOffset in="noise" result="flow"><animate attributeName="dy" values="-28;28;-28" dur="12s" repeatCount="indefinite" calcMode="spline" keyTimes="0;.5;1" keySplines=".42 0 .58 1;.42 0 .58 1"/></feOffset>
<feDisplacementMap in="SourceGraphic" in2="flow" scale="22" xChannelSelector="R" yChannelSelector="G"><animate attributeName="scale" values="14;30;14" dur="12s" repeatCount="indefinite"/></feDisplacementMap>
</filter>
<mask id="smoke" maskUnits="userSpaceOnUse" x="0" y="0" width="1024" height="1536">
<rect width="1024" height="1536" fill="white"/>
<g fill="black" filter="url(#soft)">
<path d="M185 407L304 356 365 428 414 354 490 388 513 492 581 468 642 565 606 641 648 730 605 917 545 1006 460 1048 359 1044 319 968 224 988 170 949 178 857 55 824 48 749 103 679 51 607 77 522 134 486 190 515Z"/>
<path d="M660 598L750 574 787 629 829 593 895 636 901 701 948 704 987 783 956 855 1004 913 981 1013 943 1024 952 1096 872 1138 804 1103 736 1148 652 1112 643 1051 581 1020 529 946 550 862 525 813 558 762 597 759 577 706 617 651 659 668Z"/>
</g></mask>
<radialGradient id="light"><stop stop-color="#fff" stop-opacity=".16"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
</defs>
<style>
.still{display:none}
.intro{animation:appear .25s cubic-bezier(.16,1,.3,1) both}
@keyframes appear{from{opacity:.65}to{opacity:1}}
@media(prefers-reduced-motion:reduce){.still{display:none}
.still{display:inline}.intro{animation:none}.moving{display:none}.camera{transform:none}}
</style>
<rect width="1080" height="1920" fill="#000000"/>
<g class="intro">
<g transform="translate(540 960)">
<g class="camera">
<animateTransform attributeName="transform" type="scale" values="1;1.04;1" dur="12s" repeatCount="indefinite" calcMode="spline" keyTimes="0;.5;1" keySplines=".42 0 .58 1;.42 0 .58 1"/>
<g class="camera">
<animateTransform attributeName="transform" type="translate" values="0 0;-4 -16;0 0" dur="12s" repeatCount="indefinite" calcMode="spline" keyTimes="0;.5;1" keySplines=".42 0 .58 1;.42 0 .58 1"/>
<g transform="translate(-512 -768)">
<g filter="url(#color)"><use class="still" xlink:href="#original"/><use class="moving" mask="url(#smoke)" xlink:href="#original"/>
<g class="moving" mask="url(#smoke)"><g filter="url(#vapor)"><use xlink:href="#original"/></g></g>
<g class="moving"><animateTransform attributeName="transform" type="rotate" values="-9 350 700;9 350 700;-9 350 700" dur="4s" repeatCount="indefinite" calcMode="spline" keyTimes="0;.5;1" keySplines=".42 0 .58 1;.42 0 .58 1"/><g mask="url(#iceClip)"><use xlink:href="#original"/></g></g>
<g class="moving"><animateTransform attributeName="transform" type="rotate" values="12 795 867;-12 795 867;12 795 867" dur="4s" repeatCount="indefinite" calcMode="spline" keyTimes="0;.5;1" keySplines=".42 0 .58 1;.42 0 .58 1"/><g mask="url(#metalClip)"><use xlink:href="#original"/></g></g>
</g>
<g class="moving" style="mix-blend-mode:screen">
<ellipse cx="280" cy="650" rx="170" ry="300" fill="url(#light)" opacity=".12"><animate attributeName="opacity" values=".12;.44;.12" dur="6s" repeatCount="indefinite"/></ellipse>
<ellipse cx="807" cy="878" rx="130" ry="215" fill="url(#light)" opacity=".3"><animate attributeName="opacity" values=".3;.08;.3" dur="6s" repeatCount="indefinite"/></ellipse>
</g></g></g></g></g></g></svg>'''.replace('SOURCE',source)
(p/'ENGRANAJES_INTRO_V2.svg').write_text(svg)
