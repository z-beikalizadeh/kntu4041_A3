// 1. تعریف لایه پایه (نقشه خیابان‌های باز)
var baseLayer = new ol.layer.Tile({
    source: new ol.source.OSM()
});

// 2. تعریف لایه WMS از ژئوسرور 
var wmsSource = new ol.source.TileWMS({
    url: 'http://localhost:8080/geoserver/wms',
    params: {
        'LAYERS': 'ne:countries', //استفاده از لایه کشورهای جهان 
        'TILED': true
    },
    serverType: 'geoserver',
    crossOrigin: 'anonymous'
});

var wmsLayer = new ol.layer.Tile({
    source: wmsSource
});

// 3. ساخت نقشه و تنظیم نمایش روی کل دنیا
var view = new ol.View({
    center: [0, 0], // مرکز نقشه روی خط استوا
    zoom: 2         // زوم عقب برای دیدن کل دنیا
});

var map = new ol.Map({
    target: 'map',
    layers: [baseLayer, wmsLayer],
    view: view
});

// 4. قابلیت کلیک و گرفتن اطلاعات (GetFeatureInfo)
map.on('singleclick', function(evt) {
    document.getElementById('info').innerHTML = "در حال دریافت اطلاعات از کشور مورد نظر...";
    
    var viewResolution = view.getResolution();
    var url = wmsSource.getFeatureInfoUrl(
        evt.coordinate,
        viewResolution,
        'EPSG:3857',
        {'INFO_FORMAT': 'application/json'}
    );

    if (url) {
        fetch(url)
            .then(function(response) { return response.json(); })
            .then(function(json) {
                var features = json.features;
                if (features.length > 0) {
                    var props = features[0].properties;
                    // نمایش نام کشور و قاره (این فیلدها در لایه ne:countries وجود دارند)
                    var html = '<h3>اطلاعات منطقه:</h3>';
                    html += '<p><b>نام کشور:</b> ' + (props.NAME || props.admin || 'نامشخص') + '</p>';
                    html += '<p><b>قاره:</b> ' + (props.CONTINENT || 'نامشخص') + '</p>';
                    document.getElementById('info').innerHTML = html;
                } else {
                    document.getElementById('info').innerHTML = "روی خشکی کلیک کنید.";
                }
            })
            .catch(function() {
                document.getElementById('info').innerHTML = "خطا در ارتباط با ژئوسرور. مطمئن شوید افزونه CORS در کروم فعال است.";
            });
    }
});