from setting import *
import torch.optim as optim
from tqdm import tqdm
from dataLoader import *
from model import *

def train(dataset, model, optimizer, scheduler, criterion):
    # 학습 중 학습데이터 및 검증데이터에 대한 손실값을 출력하기 위한 변수
    epoch_train_loss = 0.0
    epoch_val_loss = 0.0
    # 학습 중 손실값 혹은 metric 적용에 대한 결과값 등을 기록해두기 위한 리스트
    logs=[]
    # 학습을 시작할 epoch 지정
    start_epoch = 0
    weight_file = f'./models/{trace}/model_{start_epoch}.pth'
    # pretrained model load
    if start_epoch!=0:
        pre_weights = torch.load(weight_file, map_location=args.device)
        model.load_state_dict(pre_weights)
        
    for epoch in range(start_epoch, args.num_epoch):
        epoch_train_loss = 0.0
        epoch_val_loss = 0.0
        
        dataset.set_split('train')
        train_batch_generator = generate_batches(dataset, batch_size=args.batch_size, device=args.device)
        total = dataset.get_num_batches(args.batch_size)
        train_iterator = tqdm(train_batch_generator, desc="Training (X / X Steps) (loss=X.X)", dynamic_ncols=True)

        for batch_idx, batch_dict in enumerate(train_iterator):
            optimizer.zero_grad()
            y_pred = model(batch_dict['x_data'].to(args.device))
            loss = criterion(y_pred, batch_dict['y_target'].squeeze().to(args.device))
            epoch_train_loss += loss.item()
            train_iterator.set_description("Training (%d / %d Steps) (loss=%2.5f)" %(batch_idx, total, loss))
            loss.backward()
            optimizer.step()

        # validation
        if(epoch+1) % 1 == 0:
            dataset.set_split('val')
            val_batch_generator = generate_batches(dataset, batch_size=args.batch_size, device=args.device)
            val_iterator = tqdm(val_batch_generator, desc="Validation (X / X Steps) (loss=X.X)", dynamic_ncols=True)
            for batch_idx, batch_dict in enumerate(val_iterator):
                with torch.no_grad():
                    output = model(batch_dict['x_data'].to(args.device))
                    loss = criterion(output, batch_dict['y_target'].squeeze().to(args.device))
                    epoch_val_loss += loss.item()
                    val_iterator.set_description("Validation (%d / %d Steps) (loss=%2.5f)" %(batch_idx, total, loss))

        scheduler.step(epoch_val_loss/dataset.get_num_batches(args.batch_size))
        # scheduler.step()
        log_epoch = {'epoch':epoch+1, 'train_loss':epoch_train_loss, 'val_loss':epoch_val_loss}
        logs.append(log_epoch)
        log_df = pd.DataFrame(logs)
        log_df.to_csv(f"./logs/{trace}_log_output.csv")
        
        # model save
        if(epoch+1) % 5 == 0:
            torch.save(model.state_dict(), f'./models/{trace}/model_'+str(epoch+1)+'.pth')
    
if __name__=='__main__':
    set_seed_everywhere(args.seed, args.cuda)
    dataset_df = load_data("train/val")
    vocabset_df = load_data("vocab")
    testset_df = load_data("test")
    
    # 현재 사용가능한 디바이스로 환경변수 device 재설정
    args.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print("device:", args.device)
    # 학습에 사용할 데이터셋 파일 가져와서 Dataset 객체 만들기 
    dataset = CstateDataset.load_dataset_and_make_vectorizer(dataset_df, vocabset_df, testset_df, args.train_cstate_len, args.data_cstate_len - args.train_cstate_len)
    # dataset 객체를 만들면 안에서 vectorizer 객체도 생성되기 때문에 여기서 vectorizer 뽑아낼 수 있음
    vectorizer = dataset.get_vectorizer()

    model = Prefetcher(args, len(vectorizer.pa_vocab)).to(args.device)
   
    optimizer = optim.Adam(model.parameters(), lr=args.lr)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer=optimizer, mode='min', factor=0.5, patience=1)
    criterion = nn.NLLLoss()

    train(dataset, model, optimizer, scheduler, criterion)