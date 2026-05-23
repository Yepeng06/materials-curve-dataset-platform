import { useEffect, useMemo, useState } from 'react'

type PreviewItem={image_path:string;annotation_path:string;csv_paths:string[];annotation:Record<string,unknown>}
type TemplateItem={template_id:string;template_name:string;description?:string;default_parameters?:Record<string,unknown>;key_effects?:string[]}
type PreviewParams={mode:'explicit'|'probabilistic';template_id:string;preview_count:number;seed:number;grid:boolean;x_label:string;x_unit:string;y_label:string;y_unit:string;num_curves:number;curve_shape:string;points_per_curve:number;noise_level:number;line_style:string;line_width:number;marker:string;legend_position:string;template_defaults_applied?:boolean}
const defaults:PreviewParams={mode:'explicit',template_id:'real_mainstream',preview_count:3,seed:20260520,grid:false,x_label:'Creep time',x_unit:'h',y_label:'Creep strain',y_unit:'%',num_curves:3,curve_shape:'near_linear',points_per_curve:160,noise_level:0.02,line_style:'solid',line_width:1.5,marker:'none',legend_position:'inside_upper_right',template_defaults_applied:false}

export default function App(){const[items,setItems]=useState<PreviewItem[]>([]);const[templates,setTemplates]=useState<TemplateItem[]>([]);const[params,setParams]=useState<PreviewParams>(defaults);const[requestSnapshot,setRequestSnapshot]=useState<PreviewParams|null>(null);const[actualSnapshot,setActualSnapshot]=useState<Record<string,unknown>|null>(null);const[expandedJson,setExpandedJson]=useState<Record<number,boolean>>({});
useEffect(()=>{fetch('http://127.0.0.1:8000/templates').then(r=>r.json()).then(d=>setTemplates(d.items??[]))},[])
const currentTemplate=useMemo(()=>templates.find(t=>t.template_id===params.template_id),[templates,params.template_id])
const applyTemplateDefaults=()=>{const d=currentTemplate?.default_parameters??{};setParams(p=>({...p,...d,template_defaults_applied:true} as PreviewParams))}
const generatePreview=async()=>{const payload={...params};setRequestSnapshot(payload);const res=await fetch('http://127.0.0.1:8000/preview',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});const data=await res.json();setItems(data.items??[]);const first=data.items?.[0]?.annotation?.style?.actual_parameters;setActualSnapshot(first??null);setExpandedJson({})}
const copyJson=async (a:Record<string,unknown>)=>navigator.clipboard.writeText(JSON.stringify(a,null,2))
return <main><h1>Materials Curve Dataset Platform</h1><label>模板<select value={params.template_id} onChange={e=>setParams({...params,template_id:e.target.value})}>{templates.map(t=><option key={t.template_id} value={t.template_id}>{t.template_name}</option>)}</select></label><button onClick={applyTemplateDefaults}>应用模板默认参数</button>
<p>{currentTemplate?.description}</p><p>{(currentTemplate?.key_effects??[]).join('；')}</p>
<p>{params.mode==='probabilistic'?'当前为概率采样模式，将主要依据模板概率分布生成，部分手动参数不会生效。':'当前为显式指定模式，将优先使用下方手动参数。'}</p>
<button onClick={generatePreview}>生成预览图</button>
<details><summary>本次请求参数</summary><pre>{JSON.stringify(requestSnapshot??params,null,2)}</pre></details>
<details><summary>当前实际生效参数</summary><pre>{JSON.stringify(actualSnapshot??{},null,2)}</pre></details>
{items.map((it,idx)=>{const ann=it.annotation;const style=(ann.style??{}) as Record<string,unknown>;const ds=(ann.dataset_info??{}) as Record<string,unknown>;const actual=(style.actual_parameters??{}) as Record<string,unknown>;return <article key={idx}><img src={`http://127.0.0.1:8000/${it.image_path}`} /><p>模板：{String(ds.template_name??'-')} | 模式：{String(ds.mode??'-')} | 曲线条数：{String(actual.num_curves??'-')} | 曲线形态：{String(actual.curve_shape??'-')} | 线型：{String(actual.line_style??'-')} | 标记点：{String(actual.marker??'-')} | 网格：{String(actual.grid??'-')} | 图例位置：{String(actual.legend_position??'-')}</p><p>图片：{it.image_path.split('/').slice(-2).join('/')}，标注：{it.annotation_path.split('/').slice(-2).join('/')}</p><button onClick={()=>setExpandedJson(p=>({...p,[idx]:!p[idx]}))}>{expandedJson[idx]?'隐藏 MCG-JSON':'查看完整 MCG-JSON'}</button><button onClick={()=>copyJson(ann)}>复制 MCG-JSON</button>{expandedJson[idx]&&<pre style={{maxHeight:300,overflow:'auto'}}>{JSON.stringify(ann,null,2)}</pre>}</article>})}
</main>}
