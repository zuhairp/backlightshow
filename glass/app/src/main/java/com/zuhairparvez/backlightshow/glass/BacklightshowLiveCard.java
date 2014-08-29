package com.zuhairparvez.backlightshow.glass;

import com.google.android.glass.timeline.LiveCard;
import com.google.android.glass.timeline.LiveCard.PublishMode;
import com.loopj.android.http.AsyncHttpClient;
import com.loopj.android.http.JsonHttpResponseHandler;
import com.loopj.android.http.RequestParams;
import com.loopj.android.http.TextHttpResponseHandler;

import android.app.PendingIntent;
import android.app.Service;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.Color;
import android.os.Handler;
import android.os.IBinder;
import android.speech.RecognizerIntent;
import android.util.Log;
import android.widget.RemoteViews;

import org.apache.http.Header;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;

/**
 * A {@link Service} that publishes a {@link LiveCard} in the timeline.
 */
public class BacklightshowLiveCard extends Service {

    private static final String LIVE_CARD_TAG = "BacklightshowLiveCard";
    public static final String SERVER_ADDRESS = "http://192.168.1.65:8080/controller";

    private LiveCard mLiveCard;
    private RemoteViews liveCardView;

    private final Handler handler = new Handler();
    private final CurrentColorUpdater ccu = new CurrentColorUpdater();
    private static final long UPDATE_TIME = 10000;

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        ArrayList<String> voiceResults = intent.getExtras()
                .getStringArrayList(RecognizerIntent.EXTRA_RESULTS);
        Log.d("BLS", "Color: "+voiceResults.get(0));
        setLightColor(voiceResults.get(0));

        if (mLiveCard == null) {
            mLiveCard = new LiveCard(this, LIVE_CARD_TAG);
            liveCardView = new RemoteViews(getPackageName(), R.layout.backlightshow_live_card);
            liveCardView.setImageViewBitmap(R.id.current_color, solidColorBitmap(Color.BLACK));
            mLiveCard.setViews(liveCardView);
            handler.post(ccu);

            // Display the options menu when the live card is tapped.
            Intent menuIntent = new Intent(this, LiveCardMenuActivity.class);
            mLiveCard.setAction(PendingIntent.getActivity(this, 0, menuIntent, 0));
            mLiveCard.publish(PublishMode.REVEAL);
        } else {
            mLiveCard.navigate();
        }
        return START_STICKY;
    }


    private Bitmap solidColorBitmap(int color){
        Bitmap image = Bitmap.createBitmap(100, 100, Bitmap.Config.ARGB_8888);
        image.eraseColor(color);
        return image;
    }

    private void setLightColor(String color){
        String url = SERVER_ADDRESS;
        RequestParams rp = new RequestParams("color", color);
        AsyncHttpClient ahc = new AsyncHttpClient();

        ahc.put(url, rp, new TextHttpResponseHandler() {
            @Override
            public void onFailure(int statusCode, Header[] headers, String responseString, Throwable throwable) {
                Log.e("BLS", throwable.getMessage());
            }

            @Override
            public void onSuccess(int statusCode, Header[] headers, String responseString) {
                Log.e("BLS", "Successfully set color");
                updateLightColor();
            }
        });
    }

    private void updateLightColor(){
        AsyncHttpClient ahc = new AsyncHttpClient();
        ahc.get(SERVER_ADDRESS, new JsonHttpResponseHandler(){
            @Override
            public void onSuccess(int statusCode, Header[] headers, JSONObject response) {
                try {
                    if(liveCardView == null) return;
                    String colorHex = response.getString("color");
                    int color = Color.parseColor(colorHex);
                    liveCardView.setImageViewBitmap(R.id.current_color, solidColorBitmap(color));
                    mLiveCard.setViews(liveCardView);

                } catch (JSONException e) {
                    e.printStackTrace();
                }
            }
        });
    }

    @Override
    public void onDestroy() {
        if (mLiveCard != null && mLiveCard.isPublished()) {
            mLiveCard.unpublish();
            mLiveCard = null;
        }
        super.onDestroy();
    }

    private class CurrentColorUpdater implements Runnable{
        public boolean isStopped = false;
        @Override
        public void run() {
            if(!isStopped){
                updateLightColor();
                handler.postDelayed(ccu, UPDATE_TIME);
            }
        }
    }
}
