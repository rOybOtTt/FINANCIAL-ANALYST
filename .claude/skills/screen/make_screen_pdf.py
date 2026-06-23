# -*- coding: utf-8 -*-
"""Render a one-page company 'worth-a-look' screen to PDF (amkr.pdf palette).

Usage:  python make_screen_pdf.py <data.json> <out.pdf>

data.json schema (all strings unless noted):
{
  "ticker": "NVDA", "name": "NVIDIA Corporation",
  "asof": "2026-06-22", "price": "$209.91",
  "verdict": "WORTH A LOOK" | "WATCH" | "PASS",
  "stance": "LONG-biased, two-sided",
  "thesis": "one-line thesis",
  "bull": ["point", ...],      "bear": ["point", ...],   (4-6 each)
  "driver": "the single technical/structural driver",
  "valuation": "valuation snapshot",
  "entry": "entry / levels note",
  "risk": "what would flip the call",
  "footnote": "source / as-of / caveat line"
}
"""
import sys, json, textwrap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch

NAVY="#1F2D5A"; BLUE="#1B6CB5"; PALE="#F4F8FE"; GREEN="#2E7D32"; AMBER="#E69500"
RED="#C0392B"; SKY="#5B9BD5"; GRAY="#5A5A5A"; LBLUE="#C9D8F0"

def vcolor(v):
    v=(v or "").upper()
    if any(k in v for k in ("PASS","AVOID","SHORT","NO-GO","SKIP")): return RED
    if "WATCH" in v: return AMBER
    return GREEN

def draw_bullets(ax, items, x, y_top, colw, color, fs=9.3, lh=0.0150, wrap=58, max_lines=26):
    """draw a bulleted list top-down; returns bottom y. wraps + clips to max_lines."""
    y=y_top; lines_used=0
    for it in items:
        wrapped=textwrap.wrap(it, width=wrap) or [""]
        # bullet dot on first line
        ax.text(x, y, "•", color=color, fontsize=fs+1, fontweight="bold", va="top", ha="left")
        for k, ln in enumerate(wrapped):
            if lines_used>=max_lines:
                ax.text(x+0.012, y, "…", color=GRAY, fontsize=fs, va="top", ha="left");
                return y-lh
            ax.text(x+0.014, y, ln, color="#222222", fontsize=fs, va="top", ha="left")
            y-=lh; lines_used+=1
        y-=lh*0.35  # gap between bullets
    return y

def render(d, out):
    plt.rcParams["font.family"]="DejaVu Sans"
    fig=plt.figure(figsize=(8.5,11)); fig.patch.set_facecolor("white")
    ax=fig.add_axes([0,0,1,1]); ax.axis("off"); ax.set_xlim(0,1); ax.set_ylim(0,1)
    M=0.055; W=1-2*M
    ax.add_patch(Rectangle((0,0),1,1,color=PALE,zorder=0))
    # corner motif (bottom-left only; top is occupied by the navy band)
    ax.add_patch(plt.Polygon([(0,0.045),(0.10,0.045),(0,0.12)],color=LBLUE,zorder=0))

    # ---- top band ----
    ax.add_patch(Rectangle((0,0.905),1,0.095,color=NAVY,zorder=1))
    ax.text(M,0.957,d["ticker"],color="white",fontsize=30,fontweight="bold",va="center",zorder=2)
    ax.text(M+0.155,0.963,d.get("name",""),color=LBLUE,fontsize=12.5,va="center",zorder=2)
    ax.text(M+0.155,0.938,f"{d.get('stance','')}   ·   {d.get('price','')}   ·   as-of {d.get('asof','')}",
            color="#9FB6DE",fontsize=9.5,va="center",zorder=2)
    # verdict chip
    vc=vcolor(d["verdict"]); chip_w=0.275
    ax.add_patch(FancyBboxPatch((1-M-chip_w,0.918),chip_w,0.055,
                 boxstyle="round,pad=0.004,rounding_size=0.012",color=vc,zorder=2))
    ax.text(1-M-chip_w/2,0.946,d["verdict"],color="white",fontsize=15,fontweight="bold",
            ha="center",va="center",zorder=3)
    ax.text(1-M-chip_w-0.018,0.945,"VERDICT",color=LBLUE,fontsize=8,ha="right",va="center",
            zorder=3,fontweight="bold")

    # ---- thesis ----
    y=0.885
    ax.text(M,y,"THE THESIS IN ONE LINE",color=BLUE,fontsize=9,fontweight="bold",va="top")
    y-=0.020
    for ln in textwrap.wrap(d.get("thesis",""), width=104):
        ax.text(M,y,ln,color=NAVY,fontsize=11.5,style="italic",va="top"); y-=0.0175
    y-=0.010
    ax.add_patch(Rectangle((M,y),W,0.0015,color="#D5DEEE"))
    # ---- bull / bear columns ----
    col_top=y-0.022; colw=(W-0.03)/2
    xL=M; xR=M+colw+0.03
    ax.add_patch(Rectangle((xL,col_top+0.004),colw,0.022,color=GREEN,alpha=0.92))
    ax.text(xL+0.01,col_top+0.015,"▲  BULL — why it could be worth it",color="white",fontsize=10,fontweight="bold",va="center")
    ax.add_patch(Rectangle((xR,col_top+0.004),colw,0.022,color=RED,alpha=0.92))
    ax.text(xR+0.01,col_top+0.015,"▼  BEAR — why it might not",color="white",fontsize=10,fontweight="bold",va="center")
    bcol_top=col_top-0.010
    yb_L=draw_bullets(ax,d.get("bull",[]),xL,bcol_top,colw,GREEN,wrap=52,max_lines=24)
    yb_R=draw_bullets(ax,d.get("bear",[]),xR,bcol_top,colw,RED,wrap=52,max_lines=24)
    ybot=min(yb_L,yb_R)-0.006

    # ---- driver strip ----
    ds_h=0.052
    ybot=min(ybot,0.40)
    ax.add_patch(FancyBboxPatch((M,ybot-ds_h),W,ds_h,boxstyle="round,pad=0.003,rounding_size=0.008",
                 facecolor="#EAF1FB",edgecolor=BLUE,linewidth=1.2))
    ax.text(M+0.012,ybot-0.013,"THE SINGLE DRIVER TO WATCH",color=BLUE,fontsize=8.5,fontweight="bold",va="top")
    dy=ybot-0.027
    for ln in textwrap.wrap(d.get("driver",""), width=108):
        ax.text(M+0.012,dy,ln,color=NAVY,fontsize=9.7,va="top"); dy-=0.0150
    y=ybot-ds_h-0.018

    # ---- valuation + entry two-up ----
    def kv(x,w,label,val,accent):
        ax.add_patch(Rectangle((x,y-0.058),w,0.003,color=accent))
        ax.text(x,y,label,color=accent,fontsize=8.5,fontweight="bold",va="top")
        yy=y-0.016
        for ln in textwrap.wrap(val,width=52):
            ax.text(x,yy,ln,color="#222222",fontsize=9.2,va="top"); yy-=0.0150
    kv(xL,colw,"VALUATION",d.get("valuation",""),BLUE)
    kv(xR,colw,"ENTRY / LEVELS",d.get("entry",""),GREEN)
    y-=0.082

    # ---- risk / what flips ----
    ax.add_patch(FancyBboxPatch((M,y-0.050),W,0.050,boxstyle="round,pad=0.003,rounding_size=0.008",
                 facecolor="#FBE9E7",edgecolor=RED,linewidth=1.0))
    ax.text(M+0.012,y-0.012,"WHAT WOULD FLIP THE CALL",color=RED,fontsize=8.5,fontweight="bold",va="top")
    ry=y-0.026
    for ln in textwrap.wrap(d.get("risk",""), width=108):
        ax.text(M+0.012,ry,ln,color="#3a1a14",fontsize=9.3,va="top"); ry-=0.0150

    # ---- footer ----
    ax.add_patch(Rectangle((0,0),1,0.045,color=NAVY))
    foot=d.get("footnote","")
    ax.text(M,0.0225,foot,color=LBLUE,fontsize=7.6,style="italic",va="center")
    ax.text(1-M,0.0225,"Deep-Tech Screen · points-only go/no-go",color="#9FB6DE",fontsize=7.6,
            style="italic",va="center",ha="right")

    fig.savefig(out,dpi=170,facecolor="white"); plt.close(fig)
    return out

if __name__=="__main__":
    if len(sys.argv)<3:
        print("usage: python make_screen_pdf.py <data.json> <out.pdf>"); sys.exit(1)
    d=json.load(open(sys.argv[1],encoding="utf-8"))
    print("wrote", render(d, sys.argv[2]))
