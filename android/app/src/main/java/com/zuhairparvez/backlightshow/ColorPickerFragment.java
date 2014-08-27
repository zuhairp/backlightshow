package com.zuhairparvez.backlightshow;



import android.os.Bundle;
import android.app.Fragment;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

import com.larswerkman.holocolorpicker.ColorPicker;
import com.larswerkman.holocolorpicker.SVBar;
import com.loopj.android.http.AsyncHttpClient;
import com.loopj.android.http.RequestParams;
import com.loopj.android.http.ResponseHandlerInterface;
import com.loopj.android.http.TextHttpResponseHandler;

import org.apache.http.Header;


/**
 * A simple {@link Fragment} subclass.
 * Use the {@link ColorPickerFragment#newInstance} factory method to
 * create an instance of this fragment.
 *
 */
public class ColorPickerFragment extends Fragment implements ColorPicker.OnColorChangedListener, ColorPicker.OnColorSelectedListener {
    /**
     * Use this factory method to create a new instance of
     * this fragment using the provided parameters.
     *
     * @return A new instance of fragment ColorPickerFragment.
     */
    // TODO: Rename and change types and number of parameters
    public static ColorPickerFragment newInstance() {
        ColorPickerFragment fragment = new ColorPickerFragment();
        Bundle args = new Bundle();
        fragment.setArguments(args);
        return fragment;
    }
    public ColorPickerFragment() {
        // Required empty public constructor
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (getArguments() != null) {
        }
    }

    View rootView;
    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        rootView = inflater.inflate(R.layout.fragment_color_picker, container, false);

        ColorPicker cp = (ColorPicker) rootView.findViewById(R.id.picker);
        //SVBar svb = (SVBar) rootView.findViewById(R.id.svbar);
        //cp.addSVBar(svb);

        cp.setOnColorChangedListener(this);
        cp.setOnColorSelectedListener(this);

        return rootView;
    }


    @Override
    public void onColorChanged(int i) {

    }

    @Override
    public void onColorSelected(int i) {
        int red   = (i & 0x00FF0000) >> 16;
        int green = (i & 0x0000FF00) >> 8;
        int blue  = (i & 0x000000FF);
        String hex = String.format("#%02X%02X%02X", red, green, blue);
        Log.d("BLS", hex);

        ColorPicker cp = (ColorPicker) rootView.findViewById(R.id.picker);
        cp.setOldCenterColor(i);

        AsyncHttpClient ahc = new AsyncHttpClient();
        RequestParams rp = new RequestParams();
        rp.add("color", hex);
        ahc.put("http://192.168.1.104:8080/controller", rp, new TextHttpResponseHandler() {
            @Override
            public void onFailure(int statusCode, Header[] headers, String responseString, Throwable throwable) {
                Log.e("BLS", "Error: "+statusCode+" "+throwable.getMessage());
            }

            @Override
            public void onSuccess(int statusCode, Header[] headers, String responseString) {
                Log.d("BLS", "Success!");
            }
        });

    }
}
