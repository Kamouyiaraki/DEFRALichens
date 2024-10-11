const results = [
    ['Url', 'Anchor Text', 'External']
];
var urls = document.getElementsByTagName('a');
for (urlIndex in urls) {
    const url = urls[urlIndex]
    const externalLink = url.host !== window.location.host
    if(url.href && url.href.indexOf('://')!==-1) results.push([url.href, url.text, externalLink]) // url.rel
}
const csvContent = results.map((line)=>{
    return line.map((cell)=>{
        if(typeof(cell)==='boolean') return cell ? 'TRUE': 'FALSE'
        if(!cell) return ''
        let value = cell.replace(/[\f\n\v]*\n\s*/g, "\n").replace(/[\t\f ]+/g, ' ');
        value = value.replace(/\t/g, ' ').trim();
        return `"${value}"`
    }).join('\t')
}).join("\n");
console.log(csvContent) 
