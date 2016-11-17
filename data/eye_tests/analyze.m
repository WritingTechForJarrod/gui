x_res = 1920;
y_res = 1280;
m1 = csvread('static_1x4_letters_WOAT_1.txt');
m2 = csvread('static_1x4_letters_WOAT_2.txt');
m3 = csvread('static_1x4_letters_O_1.txt');
m4 = csvread('static_1x4_letters_O_2.txt');
m5 = csvread('static_1x4_letters_T_1.txt');
m6 = csvread('static_1x4_letters_T_2.txt');
m7 = csvread('static_1x4_letters_W_1.txt');
m8 = csvread('static_1x4_letters_W_2.txt');
m9 = csvread('static_1x4_letters_TAOW_1.txt');
m10 = csvread('static_1x4_letters_TAOW_2.txt');
m11 = csvread('static_single_letter_center_screen_1.txt');
m12 = csvread('static_single_letter_center_screen_2.txt');
m13 = csvread('static_2x2_letters_W_1.txt');
m14 = csvread('static_2x2_letters_W_2.txt');
m15 = csvread('static_2x2_letters_O_1.txt');
m16 = csvread('static_2x2_letters_O_2.txt');
m17 = csvread('static_2x2_letters_T_1.txt');
m18 = csvread('static_2x2_letters_T_2.txt');
m19 = csvread('static_2x2_letters_W_1.txt');
m20 = csvread('static_2x2_letters_W_2.txt');
m1x4 = [m3' m4' m5' m6' m7' m8' m9' m10']';
m1x1 = [m11' m12']';
m2x2 = [m13' m14' m15' m16' m17' m18' m19' m20']';

m = m1x4

m(:,2) = y_res-m(:,2);
s = size(m);
x_bucket_size = 40;
y_bucket_size = 40;
hist2d = zeros(y_res/y_bucket_size,x_res/x_bucket_size);
for k = 1: (s(1)-1)
    x_bin = int16(m(k,1))/x_bucket_size;
    y_bin = int16(m(k,2))/y_bucket_size;
    if ((x_bin <= x_res/x_bucket_size) & (y_bin <= y_res/y_bucket_size))
        if ((x_bin > 0) & (y_bin > 0))
            old = hist2d(y_bin,x_bin);
            hist2d(y_bin,x_bin) = old+1;
        end
    end
    dmdt(k,:) = [m(k+1,1)-m(k,1) m(k+1,2)-m(k,2) m(k+1,3)-m(k,3)];
end
pos = m(:,1:2);
surf(hist2d,'EdgeColor','None');
scatterplot(pos);
axis([0,1920,0,1280])