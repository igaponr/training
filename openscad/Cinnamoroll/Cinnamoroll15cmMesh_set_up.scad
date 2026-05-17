// シナモロール：3Dプリント用レイアウト
// 頭の最大幅：100mm

$fn = 32; 
line_radius = 0.8; // 印刷しやすくするため少し太めに設定
lat_steps = 10;
lon_steps = 16;

// 汎用メッシュ球体モジュール
module mesh_ellipsoid(size_vec, lats, lons, wire_r) {
    scale(size_vec) {
        // 緯度線
        for (i = [1 : lats - 1]) {
            lat_angle = (i * 180 / lats) - 90;
            r = cos(lat_angle);
            z = sin(lat_angle);
            translate([0, 0, z])
                rotate_extrude()
                    translate([r, 0, 0])
                        circle(r = wire_r / max(size_vec)); 
        }
        // 経度線
        for (i = [0 : lons - 1]) {
            lon_angle = i * 360 / lons;
            rotate([0, 0, lon_angle])
                rotate([90, 0, 0])
                    rotate_extrude()
                        translate([1, 0, 0])
                            circle(r = wire_r / max(size_vec));
        }
    }
}

// --- 印刷用レイアウト配置 ---

// 1. 頭 (中央)
// Z位置を半径(35)に合わせ、底が0に来るように
translate([0, 0, 35])
    mesh_ellipsoid([50, 40, 35], lat_steps, lon_steps, line_radius);

// 2. 耳 (左右に寝かせて配置)
// 厚み(10)の半分をZに設定
translate([60, 30, 10]) 
    rotate([0, 0, 20])
    mesh_ellipsoid([40, 15, 10], 8, 12, line_radius);

translate([-60, 30, 10]) 
    rotate([0, 0, -20])
    mesh_ellipsoid([40, 15, 10], 8, 12, line_radius);

// 3. 体 (頭の後ろ側)
translate([0, 70, 25])
    mesh_ellipsoid([25, 20, 25], 10, 12, line_radius);

// 4. 手 (体の横)
translate([40, 70, 8])
    mesh_ellipsoid([8, 8, 8], 6, 8, line_radius);
translate([-40, 70, 8])
    mesh_ellipsoid([8, 8, 8], 6, 8, line_radius);

// 5. 足 (さらに外側)
translate([30, 100, 8])
    mesh_ellipsoid([10, 12, 8], 6, 8, line_radius);
translate([-30, 100, 8])
    mesh_ellipsoid([10, 12, 8], 6, 8, line_radius);

// 6. 目 (小さいので紛失注意)
translate([10, -50, 4])
    mesh_ellipsoid([4, 2, 6], 4, 6, 0.4);
translate([-10, -50, 4])
    mesh_ellipsoid([4, 2, 6], 4, 6, 0.4);