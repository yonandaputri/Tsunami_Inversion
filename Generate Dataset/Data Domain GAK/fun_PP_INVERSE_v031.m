%% ------------- fungsi untuk post-processing SWASH dan pre-processing ANN --------------- %%
clear; close all; clc;

dt 		 = 60; 			% selang waktu simulasi
DT 		 = 0.25;		% selang waktu animasi
Nt 		 = 7200/dt;	% jumlah data hasil simulasi = waktu simulasi / selang waktu simulasi
savepng  = 0;			% 1-jika anda juga menginginkan gambar plot disimpan tiap waktu terpisah; 0-tidak, cukup simpan animasi 
framepos = [2 42 1200 500];	% Parameter lokasi jendela gambar : [kiri, bawah, panjang, tinggi] dalam satuan pixel
BP1       = load('BP01.txt');     % load file text yang berisi lokasi observasi1
BP2       = load('BP02.txt');     % load file text yang berisi lokasi observasi2
BP3       = load('BP03.txt');     % load file text yang berisi lokasi observasi3
BP4       = load('BP04.txt');     % load file text yang berisi lokasi observasi4

% setting jumlah data yang akan diambil dari simulasi untuk pelatihan di mesin ANN :
NX		 = 42; 			% jumlah data yang diambil dalam arah-x
NY       = 17; 			% jumlah data yang diambil dalam arah-y
Xi       = [105000,120000];	% masukkan x-minimum dan x-maximum 
Yi       = [75000, 90000];	% masukkan y-minimum dan y-maximum
cmin     = -10;			% minimum colorbar
cmax 	 = 10; 			% maximum colorbar

% Pilih direktori simulasi
dn       = uigetdir(pwd,'');
animname = [dn,'\GAUSS_03.gif'];	% nama file animasi

%% ======================================================================================== %%
% load every file :
load([dn,'/BASE01.mat'])	% BASE file berisi Xp , Yp dan Botlev (Bottom level = batimetri = topografi dasar laut)
load([dn,'/MAIN01.mat'])	% MAIN file berisi data Watlev (Water level = muka air laut)
%load([dn,'/MAIN02.mat'])	% MAIN file berisi data X-vel dan Y-vel

% membuat colormap baru:
m  = 64;  % 64-elements is each colormap
redblue = [0,0,1; .8,.8,.8; 1,0,0];
redblue = interp1(-1:1,redblue,linspace(-1,1,m));

% membuat folder baru untuk gambar plot tiap waktu :
if savepng == 1
	mkdir(animname(1:end-4));
end

% memilih titik yang berada area pelatihan ANN
xi = linspace(Xi(1),Xi(2),NX);
yi = linspace(Yi(1),Yi(2),NY);

%xi = Xi(1):NX:Xi(2);
%yi = Yi(1):NY:Yi(2);
[xi,yi] = meshgrid(xi,yi);

% hanya memilih xi dan yi yang berada di air :
ETA = interp2(Xp,Yp,Watlev_000000_000,xi,yi);
ETA(isnan(ETA))=0;
XI  = xi(~isnan(ETA));
YI  = yi(~isnan(ETA));


% mengecek area yang datanya digunakan untuk pelatihan ANN :
%figure(2); set(gcf,'Position',[2,42,900,300]);
%hold on; 
%contourf(Xp,Yp,double(Watlev_000000_000)); shading faceted; axis tight equal;
%plot(Xi([1 2 2 1 1]),Yi([1 1 2 2 1]),'-*r','LineWidth',1.5);
%plot(XI,YI,'om','MarkerFaceColor','r','LineWidth',1.5)
%hold off;

% Pertanyaan
%ans_id = 'Tidak';
%while strcmp(ans_id,'Tidak')
%    ans_id = questdlg('Apakah titik pengambilan data untuk pelatihan ANN-nya sudah sesuai?',...
%        'Titik untuk ANN:','Ya','Tidak','Ya');
%    if strcmp(ans_id,'Tidak')
%        disp ('Ubah dulu setting untuk pelatihan ANN!')
%        title('Ubah dulu setting untuk pelatihan ANN!')
%        return;
%    end
%end
%% ======================================================================================== %%
Tp = zeros(Nt,1);					% inisiasi variabel Tp untuk menyimpan waktu simulasi
Zp1 = zeros(Nt,length(BP1(:,1))); 	% inisiasi variabel Zp untuk menyimpan data BP1
Zp2 = zeros(Nt,length(BP2(:,1))); 	% inisiasi variabel Zp untuk menyimpan data BP2
Zp3 = zeros(Nt,length(BP3(:,1))); 	% inisiasi variabel Zp untuk menyimpan data BP3
Zp4 = zeros(Nt,length(BP4(:,1))); 	% inisiasi variabel Zp untuk menyimpan data BP4
Zi = zeros(Nt,length(XI)); 			% inisiasi variabel Zi untuk data pelatihan ANN

% plot, extract/interpolasi data, animasi :
for ii = 0 : 1 : Nt
    tt = datenum(0,0,0,0,0,dt*ii); 	% waktu simulasi :
	% ambil data muka air sesuai dengan waktu simulasi :
    eval(['ETA = double(Watlev',datestr(tt,'_HHMMSS_FFF'),');']);
	% interpolasi data muka air pada titik observasi
	eta_BP1  = interp2(Xp,Yp,ETA,BP1(:,1),BP1(:,2));
    eta_BP2  = interp2(Xp,Yp,ETA,BP2(:,1),BP2(:,2));
    eta_BP3  = interp2(Xp,Yp,ETA,BP3(:,1),BP3(:,2));
    eta_BP4  = interp2(Xp,Yp,ETA,BP4(:,1),BP4(:,2));
	% interpolasi data muka air pada titik pelatihan ANN:
	eta_ANN = interp2(Xp,Yp,ETA,XI,YI);

	% Tampilkan layar :
    fprintf('%s : max elev = %1.2e and min elev = %1.2e \n',datestr(tt,'HHMMSS'),max(ETA(:)),min(ETA(:)))
  
	% tampilan plot tiap waktu
	f = figure(10);                                                     
	set(f,'Position',framepos,'Color','w');                             % set posisi gambar
	surf(Xp,Yp,ETA); shading interp;    hold on;                        % gambar water level
	plot3(BP1(:,1),BP1(:,2),eta_BP1,'or','MarkerSize',10,'color','green'); % plot lokasi titik observasi1
    plot3(BP2(:,1),BP2(:,2),eta_BP2,'or','MarkerSize',10,'color','green'); % plot lokasi titik observasi2
    plot3(BP3(:,1),BP3(:,2),eta_BP3,'or','MarkerSize',10,'color','green'); % plot lokasi titik observasi3
    plot3(BP4(:,1),BP4(:,2),eta_BP4,'or','MarkerSize',10,'color','green'); % plot lokasi titik observasi4
	set(gca,'DataAspectRatio',[1,1,1/50]);	view(0,90);                    % setting view
    cb = colorbar; colormap(winter(10)); caxis([cmin cmax]);               % setting colorbar
    title(sprintf('water level pada saat %s',datestr(tt,'HH:MM:SS')))   % judul gambar
  	hold off    
  
    % untuk menyimpan animasi :
    set(f,'renderer','zbuffer','Color','w');
    drawnow;
    frame      = getframe(f);
    im         = frame2im(frame);
    [imind,cm] = rgb2ind(im,256,'nodither');
	if ii == 0
		imwrite(imind,cm,animname,'gif','LoopCount',Inf,'DelayTime',DT);
	else
		imwrite(imind,cm,animname,'gif','WriteMode','append','DelayTime',DT);
	end
    if savepng == 1
        imwrite(imind,cm,[animname(1:end-4),'/',datestr(tt,'HHMMSS'),'.png'],'png','BitDepth',8);
    end
    
	% simpan data yang diinterpolasi :
	Tp(ii+1,1) = dt*ii;
    Zp1(ii+1,:) = eta_BP1(:);
    Zp2(ii+1,:) = eta_BP2(:);
    Zp3(ii+1,:) = eta_BP3(:);
    Zp4(ii+1,:) = eta_BP4(:);
	Zi(ii+1,:) = eta_ANN(:);
    pause(0.1)
end

%% ======================================================================================== %%
dlmwrite([animname(1:end-4),'_ETA_Loc.txt'],[XI YI],'delimiter','\t','precision','%1.2f');  % save info lokasi titik ANN
dlmwrite([animname(1:end-4),'_ETA.txt'],Zi,'delimiter','\t','precision','%1.3e');           % save data pada titik ANN
dlmwrite([animname(1:end-4),'_BP1.txt'], [Tp Zp1],'delimiter','\t','precision','%1.3e');      % save data observasi1
dlmwrite([animname(1:end-4),'_BP2.txt'], [Tp Zp2],'delimiter','\t','precision','%1.3e');      % save data observasi2
dlmwrite([animname(1:end-4),'_BP3.txt'], [Tp Zp3],'delimiter','\t','precision','%1.3e');      % save data observasi3
dlmwrite([animname(1:end-4),'_BP4.txt'], [Tp Zp4],'delimiter','\t','precision','%1.3e');      % save data observasi4
